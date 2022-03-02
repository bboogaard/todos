from django.template import library
from django.utils.http import urlencode


register = library.Library()


@register.simple_tag(takes_context=True)
def add_page_param(context, url, param_name='page'):
    request = context.get('request')
    page = request.GET.get(param_name)
    if page and page != 1:
        params = {
            param_name: page
        }
    else:
        params = None
    return url + ('?' + urlencode(params) if params else '')
