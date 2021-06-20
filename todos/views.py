import hashlib

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic, View

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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'json_vars': {
                'items': list(
                    models.Todo.objects.active().order_by('activate_date').values_list('description', flat=True)
                ),
                'saveUrl': reverse('todos:todos_save.json')
            }
        })
        return context


class TodosSaveJson(AccessMixin, View):

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        items = request.POST.getlist('items', [])
        todos = {
            hashlib.md5(item.encode()).hexdigest(): item
            for item in items
        }
        todos_in_db = models.Todo.objects.in_bulk(field_name='todo_id')
        for todo_id, item in todos.items():
            if todo_id not in todos_in_db:
                todo = models.Todo(description=item, todo_id=todo_id)
                todo.save()
            elif todos_in_db[todo_id].is_inactive:
                todos_in_db[todo_id].activate()
        for todo_id, todo in todos_in_db.items():
            if todo_id not in todos:
                todo.soft_delete()
        return JsonResponse(data={})


class SettingsSave(AccessMixin, View):

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        form = forms.SettingsForm(request.POST or None)
        if form.is_valid():
            print(form.cleaned_data)
            cache_settings.save(**form.cleaned_data)

        return redirect(reverse('todos:index'))
