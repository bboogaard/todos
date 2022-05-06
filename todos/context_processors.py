from constance import config
from django.urls import reverse

from lib.utils import with_camel_keys


def wallpapers(request):
    return {
        'background_vars': with_camel_keys({
            'gallery': config.gallery,
            'urls': {
                'list': reverse('api:backgrounds-list')
            }
        })
    }
