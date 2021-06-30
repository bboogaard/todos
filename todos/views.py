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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'json_vars': {
                'items': TodosServiceFactory.create().get_active(),
                'saveUrl': reverse('todos:todos_save.json')
            }
        })
        return context


class TodosSaveJson(AccessMixin, View):

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        items = request.POST.getlist('items', [])
        TodosServiceFactory.create().save(items)
        return JsonResponse(data={})


class SettingsSave(AccessMixin, View):

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        form = forms.SettingsForm(request.POST or None)
        if form.is_valid():
            cache_settings.save(**form.cleaned_data)

        return redirect(reverse('todos:index'))
