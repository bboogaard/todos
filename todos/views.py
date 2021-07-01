from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic, View

from services.todos.factory import TodosServiceFactory
from todos import forms
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
        form = self.get_form(request.GET or None)
        if form.is_valid():
            items = TodosServiceFactory.create().search(form.cleaned_data['q'])
            searching = True
        else:
            items = TodosServiceFactory.create().get_active()
            searching = False
        context = self.get_context_data(
            form=form,
            searching=searching,
            json_vars={
                'items': items,
                'saveUrl': reverse('todos:todos_save.json'),
                'activateUrl': reverse('todos:todos_activate.json')
            }
        )
        return self.render_to_response(context)

    def get_form(self, data=None):
        return forms.SearchForm(data)


class TodosSaveJson(AccessMixin, View):

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        items = request.POST.getlist('items', [])
        TodosServiceFactory.create().save(items)
        return JsonResponse(data={})


class TodosActivateJson(AccessMixin, View):

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        items = request.POST.getlist('items', [])
        TodosServiceFactory.create().activate(items)
        return JsonResponse(data={})


class SettingsSave(AccessMixin, View):

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        form = forms.SettingsForm(request.POST or None)
        if form.is_valid():
            cache_settings.save(**form.cleaned_data)

        return redirect(reverse('todos:index'))
