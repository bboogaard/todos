import hashlib

from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.views import generic, View

from todos import models


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


class TodosList(AccessMixin, generic.ListView):

    context_object_name = 'todos'

    redirect_to_login = False

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(data={
            'items': list(context.get('todos'))
        })

    @transaction.atomic()
    def post(self, request, *args, **kwargs):
        items = request.POST.get('items', [])
        todos = {
            hashlib.md5(item.encode()).hexdigest(): item
            for item in items
        }
        todos_in_db = models.Todo.objects.in_bulk(field_name='todo_id')
        for todo_id, item in todos.items():
            if todo_id not in todos_in_db:
                todo = models.Todo(description=item, todo_id=todo_id)
                todo.save()
        for todo_id, todo in todos_in_db.items():
            if todo_id not in todos:
                todo.soft_delete()
        return JsonResponse(data={})

    def get_queryset(self):
        return models.Todo.objects.active().order_by('-activate_date')
