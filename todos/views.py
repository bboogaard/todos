from django.core.exceptions import PermissionDenied
from django.http import Http404
from django.http.response import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic, View
from haystack.generic_views import SearchView as BaseSearchView

from lib.utils import with_camel_keys
from services.cron.exceptions import JobNotFound
from services.cron.factory import CronServiceFactory
from api.data import models
from todos import forms


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


class CronView(AccessMixin, View):

    def get(self, request, job_name, *args, **kwargs):
        cron_service = CronServiceFactory.create_for_view()
        try:
            cron_service.run(job_name, force=True)
        except JobNotFound:
            raise Http404()

        return HttpResponse(cron_service.logger.get_value().encode(), content_type='text/plain')
