import calendar
import os
from datetime import date
from typing import Dict, List

from django.http.request import HttpRequest
from django.template.context import RequestContext
from django.template.defaultfilters import date as format_date
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlencode
from dateutil.relativedelta import relativedelta

from lib.utils import with_camel_keys
from services.factory import EventsServiceFactory
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
            search_query = form.cleaned_data['description']
        else:
            search_query = None

        context.update(dict(
            searching=search_query is not None,
            todo_vars=with_camel_keys({
                'urls': {
                    'list': reverse('api:todos-list'),
                    'create': reverse('api:todos-create-many'),
                    'update': reverse('api:todos-update-many'),
                    'delete': reverse('api:todos-delete-many'),
                    'activate': reverse('api:todos-activate-many'),
                },
                'search_query': search_query
            })
        ))
        return context

    def media(self):
        return {
            'js': {
                'static': (
                    'api/todos.jquery.js', 'todos.init.js'
                )
            }
        }

    def has_content(self):
        return True


class FilesWidgetRenderer(WidgetRendererService):

    template_name = 'files.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = forms.FileSearchForm(self.request.GET or None)
        if form.is_valid():
            search_query = form.cleaned_data['id']
        else:
            search_query = None

        context.update(dict(
            searching=search_query is not None,
            file_vars=with_camel_keys({
                'urls': {
                    'list': reverse('api:files-list'),
                    'delete': reverse('api:files-delete-one'),
                },
                'search_query': search_query
            })
        ))
        return context

    def media(self):
        return {
            'js': {
                'static': (
                    'api/files.jquery.js', 'files.init.js'
                )
            }
        }

    def has_content(self):
        return True


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
        return True


class NotesWidgetRenderer(WidgetRendererService):

    template_name = 'notes.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = forms.NoteSearchForm(self.request.GET or None)
        if form.is_valid():
            search_query = form.cleaned_data['id']
        else:
            search_query = None

        context.update(dict(
            searching=search_query is not None,
            note_vars=with_camel_keys({
                'urls': {
                    'list': reverse('api:notes-list'),
                    'create': reverse('api:notes-create-one'),
                    'update': reverse('api:notes-update-one'),
                    'delete': reverse('api:notes-delete-one'),
                },
                'search_query': search_query
            })
        ))
        return context

    def media(self):
        return {
            'js': {
                'static': (
                    'js.cookie.min.js', 'api/notes.jquery.js', 'notes.init.js'
                )
            }
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context.update(dict(
            snippet_vars=with_camel_keys({
                'urls': {
                    'list': reverse('api:snippets-list'),
                    'create': reverse('api:snippets-create-one'),
                    'update': reverse('api:snippets-update-one'),
                    'delete': reverse('api:snippets-delete-one'),
                }
            })
        ))
        return context

    def media(self):
        return {
            'js': {
                'static': (
                    'easymde/js/easymde.min.js', 'api/snippet.jquery.js', 'snippet.init.js'
                )
            },
            'css': ('easymde/css/easymde.min.css',)
        }

    def has_content(self):
        return True


class UploadWidgetRenderer(WidgetRendererService):

    template_name = 'upload.html'

    def media(self):
        return {
            'js': {
                'static': (
                    'dropzone/dropzone.min.js', 'upload.init.js'
                )
            },
            'css': ('dropzone/dropzone.min.css',)
        }

    def has_content(self):
        return True
