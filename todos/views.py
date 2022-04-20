import datetime
from io import BytesIO

from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.http.response import JsonResponse, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect
from django.template.context import RequestContext
from django.urls import reverse
from django.views import generic, View
from haystack.generic_views import SearchView as BaseSearchView

from api.data.models import PrivateImage
from services.cron.exceptions import JobNotFound
from services.cron.factory import CronServiceFactory
from services.export.factory import ExportServiceFactory, FileExportServiceFactory
from services.widgets.factory import WidgetRendererFactory
from todos import forms, models
from todos.templatetags.url_tags import add_page_param


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


class TodosExportView(AccessMixin, View):

    def get(self, request, *args, **kwargs):
        fh = ExportServiceFactory.todos().dump()
        response = HttpResponse(fh.read(), content_type='text/plain')
        response['Content-disposition'] = 'attachment'
        return response


class NotesExportView(AccessMixin, View):

    def get(self, request, *args, **kwargs):
        fh = ExportServiceFactory.notes().dump()
        response = HttpResponse(fh.read(), content_type='text/plain')
        response['Content-disposition'] = 'attachment'
        return response


class CodeSnippetsExportView(AccessMixin, View):

    def get(self, request, *args, **kwargs):
        fh = ExportServiceFactory.snippets().dump()
        response = HttpResponse(fh.read(), content_type='text/plain')
        response['Content-disposition'] = 'attachment'
        return response


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

    def dispatch(self, request, *args, **kwargs):
        self.file_type = kwargs['file_type']
        return super().dispatch(request, *args, **kwargs)


class FileExportView(FileViewMixin, AccessMixin, View):

    def get(self, request, *args, **kwargs):
        fh = FileExportServiceFactory.create(self.file_type).dump()
        response = HttpResponse(fh.read(), content_type='application/zip')
        response['Content-disposition'] = 'attachment'
        return response


class ImportView(AccessMixin, generic.TemplateView):

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
            self.import_file(BytesIO(form.files['file'].read()))
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

    def import_file(self, fh):
        raise NotImplementedError()

    def get_message(self):
        return self.message

    def get_title(self):
        return self.title


class TodosImportView(ImportView):

    message = "Todo's imported"

    title = "Import todo's"

    def import_file(self, fh):
        ExportServiceFactory.todos().load(fh)


class NotesImportView(ImportView):

    message = "Notes imported"

    title = "Import notes"

    def import_file(self, fh):
        ExportServiceFactory.notes().load(fh)


class CodeSnippetsImportView(ImportView):

    message = "Code snippets imported"

    title = "Import code snippets"

    def import_file(self, fh):
        ExportServiceFactory.snippets().load(fh)


class FileImportView(FileViewMixin, ImportView):

    def import_file(self, fh):
        return FileExportServiceFactory.create(self.file_type).load(fh)

    def get_message(self):
        return "Files imported" if self.file_type == 'file' else "Images imported"

    def get_title(self):
        return "Import files" if self.file_type == 'file' else "Import images"


class WidgetListView(AccessMixin, generic.TemplateView):

    template_name = 'widgets/widget_list.html'

    def get(self, request, *args, **kwargs):
        formset = self.get_formset()
        context = self.get_context_data(formset=formset)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        formset = self.get_formset(request.POST or None)
        if formset.is_valid():
            formset.save()
            messages.add_message(request, messages.SUCCESS, 'Widgets saved')
            return redirect(reverse('todos:widget_list'))

        context = self.get_context_data(formset=formset)
        return self.render_to_response(context)

    def get_formset(self, data=None, files=None, **kwargs):
        return forms.WidgetFormSet(data, files, **kwargs)


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
        images = list(PrivateImage.objects.all())
        try:
            image_id = int(self.request.GET.get('image_id', ''))
        except ValueError:
            image_id = images[0].pk if images else 0
        context.update({
            'images': images,
            'image_id': image_id
        })
        return context


class WidgetJson(AccessMixin, View):

    def get(self, request, widget_id, *args, **kwargs):
        try:
            widget = models.Widget.objects.get(pk=widget_id)
        except models.Widget.DoesNotExist:
            return JsonResponse({}, status=404)

        renderer = WidgetRendererFactory.get_renderer(widget)
        html = renderer.render_content(RequestContext(request, {'request': request}))
        return JsonResponse({'html': html})


class DateListView(AccessMixin, generic.ListView):

    model = models.HistoricalDate

    paginate_by = 5

    template_name = 'dates/date_list.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        context['search_form'] = forms.DateSearchForm(self.request.GET or None)
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        form = forms.DateSearchForm(self.request.GET or None)
        if form.is_valid():
            data = form.cleaned_data
            month = data.get('month')
            if month:
                queryset = queryset.filter(date__month=month)
            event = data.get('event')
            if event:
                queryset = queryset.filter(event__icontains=event)
        return queryset


class DateEditMixin(generic.TemplateView):

    def get(self, request, *args, **kwargs):
        form = self.get_form()
        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        form = self.get_form(request.POST or None)
        if form.is_valid():
            form.save()
            redirect_url = reverse('todos:date_list')
            return redirect(add_page_param({'request': request}, redirect_url))

        context = self.get_context_data(form=form)
        return self.render_to_response(context)

    def get_form(self, data=None, **kwargs):
        return forms.DateForm(data, **kwargs)


class DateCreateView(AccessMixin, DateEditMixin):

    template_name = 'dates/date_create.html'


class DateUpdateView(AccessMixin, DateEditMixin):

    template_name = 'dates/date_update.html'

    def dispatch(self, request, pk, *args, **kwargs):
        self.object = get_object_or_404(models.HistoricalDate, pk=pk)
        return super().dispatch(request, *args, **kwargs)

    def get_form(self, data=None, **kwargs):
        kwargs['instance'] = self.object
        return super().get_form(data, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['date'] = self.object
        return context


class DateDeleteView(AccessMixin, View):

    def post(self, request, *args, **kwargs):
        date_ids = request.POST.getlist('date', [])
        models.HistoricalDate.objects.filter(pk__in=date_ids).delete()
        return redirect(reverse('todos:date_list'))


class CronView(AccessMixin, View):

    def get(self, request, job_name, *args, **kwargs):
        cron_service = CronServiceFactory.create_for_view()
        try:
            cron_service.run(job_name, force=True)
        except JobNotFound:
            raise Http404()

        return HttpResponse(cron_service.logger.get_value().encode(), content_type='text/plain')
