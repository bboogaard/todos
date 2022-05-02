from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.http.response import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.context import RequestContext
from django.urls import reverse
from django.views import generic, View
from haystack.generic_views import SearchView as BaseSearchView

from lib.utils import with_camel_keys
from services.cron.exceptions import JobNotFound
from services.cron.factory import CronServiceFactory
from services.widgets.factory import WidgetRendererFactory
from todos import forms, models


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


class CarouselView(AccessMixin, generic.TemplateView):

    template_name = 'carousel.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            image_id = int(self.request.GET.get('image_id', ''))
        except ValueError:
            image_id = None
        context.update(dict(
            carousel_vars=with_camel_keys({
                'urls': {
                    'list': reverse('api:carousel-list'),
                    'find_page': reverse('api:carousel-find-page')
                },
                'image_id': image_id
            })
        ))
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


class CronView(AccessMixin, View):

    def get(self, request, job_name, *args, **kwargs):
        cron_service = CronServiceFactory.create_for_view()
        try:
            cron_service.run(job_name, force=True)
        except JobNotFound:
            raise Http404()

        return HttpResponse(cron_service.logger.get_value().encode(), content_type='text/plain')
