import calendar
import os
from datetime import date
from typing import Dict, List

from constance import config
from django.http.request import HttpRequest
from django.template.context import RequestContext
from django.template.defaultfilters import date as format_date
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlencode
from dateutil.relativedelta import relativedelta

from services.factory import EventsServiceFactory, ItemServiceFactory
from todos import forms
from todos.models import HistoricalDate, PrivateFile, PrivateImage, Widget


class WidgetRendererService:

    content: str

    request: HttpRequest

    template_path: str = 'widgets'

    template_name: str

    widget: Widget

    def __init__(self, widget: Widget):
        self.widget = widget

    def render(self, context: RequestContext):
        self.request = context.get('request')
        self.content = self.render_content(context)
        if not self.has_content():
            return ''

        return render_to_string(
            'widgets/widget.html',
            {
                'content': self.content,
                'title': self.widget.title,
                'widget_id': self.widget.widget_id,
                'widget_type': self.widget.type
            },
            self.request
        )

    def render_content(self, context):
        self.request = getattr(self, 'request', context.get('request'))
        context = self.get_context_data(**context.flatten())
        return render_to_string(self.get_template(), context, self.request)

    def get_context_data(self, **kwargs):
        return kwargs

    def get_template(self):
        return os.path.join(self.template_path, self.template_name)

    def media(self):
        return {}

    def global_vars(self):
        return {}

    def has_content(self):
        raise NotImplementedError()


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
            'js': {
                'static': (
                    'checklist.provider.local.js', 'checklist.provider.remote.js', 'checklist.provider.factory.js',
                    'checklist.jquery.js', 'todos.init.js'
                )
            }
        }

    def global_vars(self):
        return {
            'provider': config.todos_provider
        }

    def has_content(self):
        return True


class FilesWidgetRenderer(WidgetRendererService):

    files: List[PrivateFile] = []

    template_name = 'files.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = forms.FileSearchForm(self.request.GET or None)
        if form.is_valid():
            self.files = PrivateFile.objects.filter(pk=form.cleaned_data['file_id'])
        else:
            self.files = PrivateFile.objects.all()

        context.update(dict(
            files=self.files
        ))
        return context

    def has_content(self):
        return bool(len(self.files))


class ImagesWidgetRenderer(WidgetRendererService):

    images: List[PrivateImage] = []

    template_name = 'images.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = forms.ImageSearchForm(self.request.GET or None)
        if form.is_valid():
            self.images = PrivateImage.objects.filter(pk=form.cleaned_data['image_id'])
        else:
            self.images = PrivateImage.objects.all()

        context.update(dict(
            images=self.images
        ))
        return context

    def media(self):
        return {
            'js': {
                'static': ('images.init.js',)
            }
        }

    def has_content(self):
        return bool(len(self.images))


class NotesWidgetRenderer(WidgetRendererService):

    template_name = 'notes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = forms.NoteSearchForm(self.request.GET or None)
        if form.is_valid():
            items = ItemServiceFactory.notes().search(form.cleaned_data['note_id'])
            index = 0
            searching = True
        else:
            items = ItemServiceFactory.notes().get_active()
            index = ItemServiceFactory.notes().get_index()
            searching = False

        context.update(
            searching=searching,
            note_vars={
                'items': items,
                'index': index,
                'saveUrl': reverse('todos:notes_save.json'),
                'searching': searching
            }
        )
        return context

    def media(self):
        return {
            'js': {
                'static': (
                    'notes.provider.local.js', 'notes.provider.remote.js', 'notes.provider.factory.js',
                    'notes.jquery.js', 'notes.init.js'
                )
            }
        }

    def global_vars(self):
        return {
            'provider': config.notes_provider
        }

    def has_content(self):
        return True


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
        prev_url = reverse('todos:index') + '?' + urlencode({
            'year': prev_dt.year,
            'month': prev_dt.month
        })
        next_url = reverse('todos:index') + '?' + urlencode({
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
            'js': {
                'static': ('events.init.js',)
            }
        }

    def global_vars(self):
        return {}

    def has_content(self):
        return True


class DatesWidgetRenderer(WidgetRendererService):

    dates: List[Dict[str, str]] = []

    template_name = 'dates.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_date = date.today()
        self.dates = [
            {
                'date': format_date(dt.date, 'j F Y'),
                'event': dt.event
            }
            for dt in HistoricalDate.objects.filter(
                date__month=current_date.month, date__day=current_date.day
            )
        ]
        context.update({
            'date': current_date,
            'date_vars': {
                'dates': self.dates
            }
        })
        return context

    def media(self):
        return {
            'js': {
                'static': (
                    'dates.jquery.js', 'dates.init.js'
                )
            }
        }

    def has_content(self):
        return bool(len(self.dates))


class CodeSnippetWidgetRenderer(WidgetRendererService):

    template_name = 'snippet.html'

    def media(self):
        return {
            'js': {
                'static': (
                    'easymde/js/easymde.min.js',
                    'snippet.jquery.js', 'snippet.init.js'
                )
            },
            'css': ('easymde/css/easymde.min.css',)
        }

    def has_content(self):
        return True
