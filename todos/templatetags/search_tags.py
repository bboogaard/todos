from django.template import library
from django.urls import reverse
from django.utils.http import urlencode


register = library.Library()


@register.simple_tag(takes_context=True)
def result_url(context, obj):
    request = context.get('request')
    url = reverse('todos:index')
    params = {
        'q': request.GET.get('q', '')
    }
    params.update(obj.result_params)
    return url + '?' + urlencode(params)
