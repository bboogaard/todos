from django.core.management import call_command
from django.template import Template
from django.template.context import RequestContext
from django.test.testcases import TestCase
from django.test.client import RequestFactory

from todos.models import Widget


class TestEventService(TestCase):

    def setUp(self):
        super().setUp()
        call_command('loaddata', 'widgets.json')

    def _render(self, html: str, **kwargs):
        tpl = Template('{% load widgets %}' + html)
        context = RequestContext(kwargs.pop('request'), kwargs)
        return tpl.render(context)

    def test_render_widget(self):
        request = RequestFactory().get('/')
        widget = Widget.objects.get(type=Widget.WIDGET_TYPE_TODOS)
        output = self._render('{% render_widget widget %}', request=request, widget=widget)
        self.assertIn('Enter item', output)

    def test_render_js(self):
        request = RequestFactory().get('/')
        widget = Widget.objects.get(type=Widget.WIDGET_TYPE_EVENTS)
        output = self._render('{% render_js widget %}', request=request, widget=widget)
        self.assertIn('events.init.js', output)

    def test_render_css(self):
        request = RequestFactory().get('/')
        widget = Widget.objects.get(type=Widget.WIDGET_TYPE_EVENTS)
        output = self._render('{% render_css widget %}', request=request, widget=widget)
        self.assertIn('calendar.css', output)
