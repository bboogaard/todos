from io import BytesIO

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views import generic, View
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
            widgets=widgets
        )
        return self.render_to_response(context)


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
        items = request.POST.getlist('items', [])
        try:
            index = int(request.POST.get('index', '0'))
        except (TypeError, ValueError):
            index = 0
        ItemServiceFactory.notes().save(items, index=index)
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


class FileListView(AccessMixin, generic.TemplateView):

    template_name = 'files/file_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'files': models.PrivateFile.objects.all()
        })
        return context


class FileCreateView(AccessMixin, generic.TemplateView):

    template_name = 'files/file_create.html'

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST or None, files=request.FILES or None)
        if form.is_valid():
            form.save()
            return redirect(reverse('todos:file_list'))

        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_form(self, data=None, files=None, **kwargs):
        return forms.FileForm(data, files=files, **kwargs)


class FileDeleteView(AccessMixin, View):

    def post(self, request, *args, **kwargs):
        file_ids = request.POST.getlist('file', [])
        qs = models.PrivateFile.objects.filter(pk__in=file_ids)
        file_names = [file.file.name for file in qs]
        qs.delete()
        for file in file_names:
            private_storage.delete(file)
        return redirect(reverse('todos:file_list'))


class FileExportView(AccessMixin, View):

    def get(self, request, *args, **kwargs):
        fh = FilesServiceFactory.create().dump('files.zip')
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
            self.service.load(BytesIO(form.files['file'].read()))
            messages.add_message(request, messages.SUCCESS, self.message)
            return redirect(request.path)

        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context

    def get_form(self, data=None, files=None, **kwargs):
        return forms.ImportForm(data, files=files, **kwargs)


class TodosImportView(ImportView):

    service = ItemServiceFactory.todos()

    message = "Todo's imported"

    title = "Import todo's"


class NotesImportView(ImportView):

    service = ItemServiceFactory.notes()

    message = "Notes imported"

    title = "Import notes"


class FileImportView(ImportView):

    service = FilesServiceFactory.create()

    message = "Files imported"

    title = "Import files"


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
