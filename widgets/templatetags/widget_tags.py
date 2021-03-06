import json

from django.template import library
from django.utils.html import mark_safe

from api.data.models import Widget
from widgets.service.factory import WidgetRendererFactory


register = library.Library()


@register.simple_tag(takes_context=True)
def render_widget(context, widget: Widget):
    renderer = WidgetRendererFactory.get_renderer(widget)
    if not renderer:
        return ''

    return renderer.render(context)


@register.inclusion_tag('widgets/js.html', takes_context=True)
def render_js(context, widget: Widget):
    renderer = WidgetRendererFactory.get_renderer(widget)
    if not renderer:
        return {
            'static_files': [],
            'external_files': [],
            'var_name': None,
            'values': None
        }

    static_files = renderer.media().get('js', {}).get('static', [])
    external_files = renderer.media().get('js', {}).get('external', [])
    global_vars = renderer.global_vars()
    return {
        'widget': widget,
        'static_files': static_files,
        'external_files': external_files,
        'var_name': '{}_vars'.format(widget.type),
        'values': mark_safe(json.dumps(global_vars))
    }


@register.inclusion_tag('widgets/css.html')
def render_css(widget: Widget):
    renderer = WidgetRendererFactory.get_renderer(widget)
    if not renderer:
        return {
            'files': []
        }

    files = renderer.media().get('css', [])
    return {
        'files': files
    }
