import calendar
import os
from datetime import date

from django.http.request import HttpRequest
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlencode
from dateutil.relativedelta import relativedelta

from api.views.internal.factory import ViewSetFactory
from lib.utils import with_camel_keys
from todos import forms
from todos.models import Widget


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
            search_query = form.cleaned_data['file_id']
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

    template_name = 'images.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = forms.ImageSearchForm(self.request.GET or None)
        if form.is_valid():
            search_query = form.cleaned_data['image_id']
        else:
            search_query = None

        context.update(dict(
            searching=search_query is not None,
            image_vars=with_camel_keys({
                'urls': {
                    'list': reverse('api:images-list'),
                    'delete': reverse('api:images-delete-one'),
                },
                'carousel_url': reverse('todos:carousel'),
                'search_query': search_query
            })
        ))
        return context

    def media(self):
        return {
            'js': {
                'static': ('api/images.jquery.js', 'images.init.js',)
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
            search_query = form.cleaned_data['note_id']
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

        # today = date.today()
        # form = forms.MonthForm(self.request.GET or None)
        # if form.is_valid():
        #     dt = date(year=form.cleaned_data['year'], month=form.cleaned_data['month'], day=1)
        # else:
        #     dt = today
        # prev_dt = dt - relativedelta(months=1)
        # prev_dt = date(prev_dt.year, prev_dt.month, 1)
        # next_dt = dt + relativedelta(months=1)
        # next_dt = date(next_dt.year, next_dt.month, calendar.monthrange(next_dt.year, next_dt.month)[1])
        # prev_url = reverse('todos:index') + '?' + urlencode({
        #     'year': prev_dt.year,
        #     'month': prev_dt.month
        # })
        # next_url = reverse('todos:index') + '?' + urlencode({
        #     'year': next_dt.year,
        #     'month': next_dt.month
        # })
        # instances = ViewSetFactory(self.request.user).event_list(
        #     {'date_range': ','.join([prev_dt.strftime('%Y-%m-%d'), next_dt.strftime('%Y-%m-%d')])}
        # )
        # events = EventsServiceFactory.create().get_events(instances, dt.year, dt.month)
        # context.update(events=events, dt=dt, prev_url=prev_url, next_url=next_url, today=today)

        today = date.today()
        context.update(dict(
            event_vars=with_camel_keys({
                'urls': {
                    'list': reverse('api:events-list'),
                    'weeks': reverse('api:events-weeks'),
                    'create': reverse('api:events-create-one'),
                    'update': reverse('api:events-update-one'),
                    'delete': reverse('api:events-delete-one'),
                },
                'year': today.year,
                'month': today.month
            })
        ))
        return context

    def media(self):
        return {
            'css': (
                'calendar.css',
                'tempus-dominus/css/font-awesome.css'
            ),
            'js': {
                'static': ('ejs.min.js', 'api/events.jquery.js', 'events.init.js',)
            }
        }

    def global_vars(self):
        return {}

    def has_content(self):
        return True


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
