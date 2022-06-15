from django.template import Template
from django.template.context import RequestContext
from django.test.testcases import TestCase
from django.test.client import RequestFactory


class TestUrlTags(TestCase):

    def _render(self, html: str, **kwargs):
        tpl = Template('{% load url_tags %}' + html)
        context = RequestContext(kwargs.pop('request'), kwargs)
        return tpl.render(context)

    def test_add_page_param(self):
        request = RequestFactory().get('/?page=2')
        output = self._render('{% add_page_param "/foo" %}', request=request)
        self.assertIn('/foo?page=2', output)

    def test_add_page_param_no_param(self):
        request = RequestFactory().get('/')
        output = self._render('{% add_page_param "/foo" %}', request=request)
        self.assertIn('/foo', output)

    def test_add_page_param_1(self):
        request = RequestFactory().get('/?page=1')
        output = self._render('{% add_page_param "/foo" %}', request=request)
        self.assertIn('/foo', output)

    def test_add_page_param_other_param(self):
        request = RequestFactory().get('/?p=2')
        output = self._render('{% add_page_param "/foo" "p" %}', request=request)
        self.assertIn('/foo?p=2', output)
