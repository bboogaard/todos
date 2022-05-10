from typing import Dict, List

from django.core.management import call_command
from django.template import Template
from django.template.context import RequestContext
from django.test.testcases import TestCase
from django.test.client import RequestFactory

from api.data.models import Widget


class TestEventService(TestCase):

    def setUp(self):
        super().setUp()
        call_command('loaddata', 'widgets.json')

    def _render(self, html: str, **kwargs):
        tpl = Template('{% load widgets %}' + html)
        context = RequestContext(kwargs.pop('request'), kwargs)
        return tpl.render(context)

    def test_render_widget(self):
        self._test_tag('{% render_widget widget %}', {
            Widget.WIDGET_TYPE_TODOS: ['Enter item']
        })

    def test_render_js(self):
        self._test_tag('{% render_js widget %}', {
            Widget.WIDGET_TYPE_TODOS: ['todos.init.js'],
            Widget.WIDGET_TYPE_FILES: ['files.init.js'],
            Widget.WIDGET_TYPE_NOTES: ['notes.init.js'],
            Widget.WIDGET_TYPE_EVENTS: ['events.init.js'],
            Widget.WIDGET_TYPE_IMAGES: ['images.init.js'],
            Widget.WIDGET_TYPE_SNIPPET: ['snippet.init.js'],
            Widget.WIDGET_TYPE_UPLOAD: ['upload.init.js']
        })

    def test_render_css(self):
        self._test_tag('{% render_css widget %}', {
            Widget.WIDGET_TYPE_EVENTS: ['calendar.css'],
        })

    def _test_tag(self, tag: str, must_contain: Dict[str, List[str]]):
        request = RequestFactory().get('/')
        for widget in Widget.objects.all():
            output = self._render(tag, request=request, widget=widget)
            self.assertTrue(all([item in output for item in must_contain.get(widget.type, [])]))
