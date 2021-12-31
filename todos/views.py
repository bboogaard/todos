import datetime
from io import BytesIO

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http.response import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic, View
from haystack.generic_views import SearchView as BaseSearchView
from private_storage.storage import private_storage

from services.api import Api
from services.factory import FilesServiceFactory, ItemServiceFactory
from todos import forms, models
from todos.settings import cache_settings


class AccessMixin(View):

    redirect_to_login = True

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            if self.redirect_to_login:
                return redirect(reverse('admin:login') + '?next=/')
            raise PermissionDenied()

        return super().dispatch(request, *args, **kwargs)


class IndexView(AccessMixin, generic.TemplateView):

    template_name = 'index.html'

    def get(self, request, *args, **kwargs):
        widgets = models.Widget.objects.filter(is_enabled=True)
        context = self.get_context_data(
            widgets=widgets,
            search_form=forms.SearchForm(request.GET or None)
        )
        return self.render_to_response(context)


class SearchView(BaseSearchView):

    form_name = 'search_form'

    form_class = forms.SearchForm


class TodosSaveJson(AccessMixin, View):

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        items = request.POST.getlist('items', [])
        ItemServiceFactory.todos().save(items)
        return JsonResponse(data={})


class TodosActivateJson(AccessMixin, View):

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        items = request.POST.getlist('items', [])
        ItemServiceFactory.todos().activate(items)
        return JsonResponse(data={})


class TodosExportView(AccessMixin, View):

    def get(self, request, *args, **kwargs):
        fh = ItemServiceFactory.todos().dump('todos.txt')
        response = HttpResponse(fh.read(), content_type='text/plain')
        response['Content-disposition'] = 'attachment'
        return response


class NotesSaveJson(AccessMixin, View):

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        searching = request.POST.get('searching', 'false') == 'true'
        items = request.POST.getlist('items', [])
        try:
            index = int(request.POST.get('index', '0'))
        except (TypeError, ValueError):
            index = 0
        ItemServiceFactory.notes().save(items, is_filtered=searching, index=index)
        return JsonResponse(data={})


class NotesExportView(AccessMixin, View):

    def get(self, request, *args, **kwargs):
        fh = ItemServiceFactory.notes().dump('notes.txt')
        response = HttpResponse(fh.read(), content_type='text/plain')
        response['Content-disposition'] = 'attachment'
        return response


class SettingsSave(AccessMixin, View):

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        form = forms.SettingsForm(request.POST or None)
        if form.is_valid():
            cache_settings.save(**form.cleaned_data)

        return redirect(reverse('todos:index'))


class WallpaperListView(AccessMixin, generic.TemplateView):

    template_name = 'wallpapers/wallpaper_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'wallpapers': models.Wallpaper.objects.order_by('gallery', 'position')
        })
        return context


class WallpaperEditMixin(generic.TemplateView):

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            form.save()
            return redirect(reverse('todos:wallpaper_list'))

        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_form(self, data=None, files=None, **kwargs):
        return forms.WallpaperForm(data, files=files, **kwargs)


class WallpaperCreateView(AccessMixin, WallpaperEditMixin):

    template_name = 'wallpapers/wallpaper_create.html'


class WallpaperUpdateView(AccessMixin, WallpaperEditMixin):

    template_name = 'wallpapers/wallpaper_update.html'

    def dispatch(self, request, pk, *args, **kwargs):
        self.object = get_object_or_404(models.Wallpaper, pk=pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, data=None, files=None, **kwargs):
        kwargs['instance'] = self.object
        return super().get_form(data, files, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['wallpaper'] = self.object
        return context


class WallpaperDeleteView(AccessMixin, View):

    def post(self, request, *args, **kwargs):
        wallpaper_ids = request.POST.getlist('wallpaper', [])
        models.Wallpaper.objects.filter(pk__in=wallpaper_ids).delete()
        return redirect(reverse('todos:wallpaper_list'))


class FileViewMixin:

    file_type = None

    model = None

    object_name = None

    object_name_plural = None

    file_field = None

    def dispatch(self, request, *args, **kwargs):
        self.file_type = kwargs['file_type']
        self.model = self.get_model(self.file_type)
        self.object_name, self.object_name_plural = {
            'file': ('File', 'Files'),
            'image': ('Image', 'Images')
        }.get(self.file_type)
        self.file_field = {
            'file': 'file',
            'image': 'image'
        }.get(self.file_type)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'file_type': self.file_type,
            'object_name': self.object_name,
            'object_name_plural': self.object_name_plural,
        })
        return context

    def get_model(self, file_type):
        return {
            'file': models.PrivateFile,
            'image': models.PrivateImage
        }.get(file_type)


class FileListView(FileViewMixin, AccessMixin, generic.TemplateView):

    template_name = 'files/file_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'files': self.model.objects.all()
        })
        return context


class FileEditMixin(FileViewMixin, generic.TemplateView):

    form_class = None

    def dispatch(self, request, *args, **kwargs):
        self.form_class = {
            'file': forms.FileForm,
            'image': forms.ImageForm
        }.get(kwargs['file_type'])
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            form.save()
            return redirect(reverse('todos:file_list', args=[self.file_type]))

        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_form(self, data=None, files=None, **kwargs):
        return self.form_class(data, files=files, **kwargs)


class FileCreateView(AccessMixin, FileEditMixin):

    template_name = 'files/file_create.html'


class FileUpdateView(AccessMixin, FileEditMixin):

    template_name = 'files/file_update.html'

    def dispatch(self, request, pk, *args, **kwargs):
        self.object = get_object_or_404(self.get_model(kwargs['file_type']), pk=pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, data=None, files=None, **kwargs):
        kwargs['instance'] = self.object
        return super().get_form(data, files, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['file'] = self.object
        return context


class FileDeleteView(FileViewMixin, AccessMixin, View):

    def post(self, request, *args, **kwargs):
        file_ids = request.POST.getlist('file', [])
        qs = self.model.objects.filter(pk__in=file_ids)
        file_names = [getattr(file, self.file_field).name for file in qs]
        qs.delete()
        for file in file_names:
            private_storage.delete(file)
        return redirect(reverse('todos:file_list', args=[self.file_type]))


class FileExportView(FileViewMixin, AccessMixin, View):

    def get(self, request, *args, **kwargs):
        fh = FilesServiceFactory.create(self.file_type).dump()
        response = HttpResponse(fh.read(), content_type='application/zip')
        response['Content-disposition'] = 'attachment'
        return response


class ImportView(AccessMixin, generic.TemplateView):

    service: Api

    message: str

    title: str

    template_name = 'import.html'

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            self.get_service().load(BytesIO(form.files['file'].read()))
            messages.add_message(request, messages.SUCCESS, self.get_message())
            return redirect(request.path)

        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.get_title()
        return context

    def get_form(self, data=None, files=None, **kwargs):
        return forms.ImportForm(data, files=files, **kwargs)

    def get_service(self):
        return self.service

    def get_message(self):
        return self.message

    def get_title(self):
        return self.title


class TodosImportView(ImportView):

    service = ItemServiceFactory.todos()

    message = "Todo's imported"

    title = "Import todo's"


class NotesImportView(ImportView):

    service = ItemServiceFactory.notes()

    message = "Notes imported"

    title = "Import notes"


class FileImportView(FileViewMixin, ImportView):

    def get_service(self):
        return FilesServiceFactory.create(self.file_type)

    def get_message(self):
        return "Files imported" if self.file_type == 'file' else "Images imported"

    def get_title(self):
        return "Import files" if self.file_type == 'file' else "Import images"


class WidgetListView(AccessMixin, generic.TemplateView):

    template_name = 'widgets/widget_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'widgets': models.Widget.objects.all()
        })
        return context


class WidgetSaveView(AccessMixin, View):

    def post(self, request, *args, **kwargs):
        widget_ids = request.POST.getlist('widget', [])
        qs = models.Widget.objects.all()
        widgets = []
        for widget in qs:
            widget.is_enabled = str(widget.pk) in widget_ids
            widgets.append(widget)
        models.Widget.objects.bulk_update(widgets, fields=['is_enabled'])
        return redirect(reverse('todos:widget_list'))


class EventCreateMixin(View):

    template_name = 'events/event_create.html'

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST or None)
        if form.is_valid():
            instance = form.save()
            return redirect(reverse('todos:event_update', kwargs={'pk': instance.pk}))

        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class EventCreateView(AccessMixin, EventCreateMixin, generic.TemplateView):

    def dispatch(self, request, *args, **kwargs):
        try:
            self.event_date = datetime.datetime.strptime(request.GET.get('event_date', ''), '%Y-%m-%d').date()
        except ValueError:
            return HttpResponseBadRequest()
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'event_date': self.event_date
        })
        return context

    def get_form(self, data=None, **kwargs):
        return forms.EventForm(data, date=self.event_date, **kwargs)


class EventUpdateView(AccessMixin, EventCreateMixin, generic.TemplateView):

    def dispatch(self, request, pk, *args, **kwargs):
        self.object = get_object_or_404(models.Event, pk=pk)
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'event_date': self.object.datetime.date()
        })
        return context

    def get_form(self, data=None, **kwargs):
        return forms.EventForm(data, date=self.object.datetime.date(), instance=self.object, **kwargs)


class EventDeleteView(AccessMixin, generic.TemplateView):

    def post(self, request, pk, *args, **kwargs):
        self.object = get_object_or_404(models.Event, pk=pk)
        self.object.delete()
        return redirect(reverse('todos:index'))


class CarouselView(AccessMixin, generic.TemplateView):

    template_name = 'carousel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        images = list(models.PrivateImage.objects.all())
        try:
            image_id = int(self.request.GET.get('image_id', ''))
        except ValueError:
            image_id = images[0].pk if images else 0
        context.update({
            'images': images,
            'image_id': image_id
        })
        return context
