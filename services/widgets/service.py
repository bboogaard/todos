import os
from datetime import date

from django.http.request import HttpRequest
from django.template.context import RequestContext
from django.template.loader import render_to_string
from django.urls import reverse

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
                    'import': reverse('api:todos-import-items'),
                },
                'search_query': search_query
            })
        ))
        return context

    def media(self):
        return {
            'js': {
                'static': (
                    'jquery.upload.js', 'api/todos.jquery.js', 'todos.init.js'
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
                    'import': reverse('api:files-import-files'),
                },
                'search_query': search_query
            })
        ))
        return context

    def media(self):
        return {
            'js': {
                'static': (
                    'jquery.upload.js', 'api/files.jquery.js', 'files.init.js'
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
                    'import': reverse('api:images-import-files'),
                },
                'carousel_url': reverse('todos:carousel'),
                'search_query': search_query
            })
        ))
        return context

    def media(self):
        return {
            'js': {
                'static': ('jquery.upload.js', 'api/images.jquery.js', 'images.init.js',)
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
                    'import': reverse('api:notes-import-items'),
                },
                'search_query': search_query
            })
        ))
        return context

    def media(self):
        return {
            'js': {
                'static': (
                    'js.cookie.min.js', 'jquery.upload.js', 'api/notes.jquery.js', 'notes.init.js'
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
                    'import': reverse('api:snippets-import-items'),
                }
            })
        ))
        return context

    def media(self):
        return {
            'js': {
                'static': (
                    'easymde/js/easymde.min.js', 'jquery.upload.js', 'api/snippet.jquery.js', 'snippet.init.js'
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
