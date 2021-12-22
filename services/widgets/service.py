import calendar
import os
from datetime import date

from django.http.request import HttpRequest
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlencode
from dateutil.relativedelta import relativedelta

from services.factory import EventsServiceFactory, ItemServiceFactory
from todos import forms
from todos.models import Widget
from todos.settings import cache_settings


class WidgetRendererService:

    request: HttpRequest

    template_path: str = 'widgets'

    template_name: str

    widget: Widget

    def __init__(self, widget: Widget):
        self.widget = widget
        self.settings = cache_settings.load()

    def render(self, context: RequestContext):
        self.request = context.get('request')
        context = self.get_context_data(**context.flatten())
        return render_to_string(self.get_template(), context, self.request)

    def get_context_data(self, **kwargs):
        kwargs.update({
            'title': self.widget.title
        })
        return kwargs

    def get_template(self):
        return os.path.join(self.template_path, self.template_name)

    def media(self):
        return {}

    def global_vars(self):
        return {}


class TodosWidgetRenderer(WidgetRendererService):

    template_name = 'todos.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = forms.TodoSearchForm(self.request.GET or None)
        if form.is_valid():
            items = ItemServiceFactory.todos().search(form.cleaned_data['description'])
            searching = True
        else:
            items = ItemServiceFactory.todos().get_active()
            searching = False

        context.update(dict(
            form=form,
            searching=searching,
            todo_vars={
                'items': items,
                'saveUrl': reverse('todos:todos_save.json'),
                'activateUrl': reverse('todos:todos_activate.json'),
                'searching': searching
            }
        ))
        return context

    def media(self):
        return {
            'js': (
                'checklist.provider.local.js', 'checklist.provider.remote.js', 'checklist.provider.factory.js',
                'checklist.jquery.js', 'todos.init.js'
            )
        }

    def global_vars(self):
        return {
            'provider': self.settings.todos_provider
        }


class FilesWidgetRenderer(WidgetRendererService):

    template_name = 'files.html'


class NotesWidgetRenderer(WidgetRendererService):

    template_name = 'notes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(
            note_vars={
                'items': ItemServiceFactory.notes().get_active(),
                'index': ItemServiceFactory.notes().get_index(),
                'saveUrl': reverse('todos:notes_save.json')
            }
        )
        return context

    def media(self):
        return {
            'js': (
                'notes.provider.local.js', 'notes.provider.remote.js', 'notes.provider.factory.js',
                'notes.jquery.js', 'notes.init.js'
            )
        }

    def global_vars(self):
        return {
            'provider': self.settings.notes_provider
        }


class EventsWidgetRenderer(WidgetRendererService):

    template_name = 'events.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        today = date.today()
        form = forms.MonthForm(self.request.GET or None)
        if form.is_valid():
            dt = date(year=form.cleaned_data['year'], month=form.cleaned_data['month'], day=1)
        else:
            dt = today
        prev_dt = dt - relativedelta(months=1)
        prev_dt = date(prev_dt.year, prev_dt.month, 1)
        next_dt = dt + relativedelta(months=1)
        next_dt = date(next_dt.year, next_dt.month, calendar.monthrange(next_dt.year, next_dt.month)[1])
        prev_url = self.request.path + '?' + urlencode({
            'year': prev_dt.year,
            'month': prev_dt.month
        })
        next_url = self.request.path + '?' + urlencode({
            'year': next_dt.year,
            'month': next_dt.month
        })
        events = EventsServiceFactory.create().get_events(dt.year, dt.month, prev_dt, next_dt)
        context.update(events=events, dt=dt, prev_url=prev_url, next_url=next_url, today=today)

        return context

    def media(self):
        return {
            'css': (
                'calendar.css',
                'tempus-dominus/css/font-awesome.css'
            ),
            'js': (
                'events.init.js',
            )
        }

    def global_vars(self):
        return {}
