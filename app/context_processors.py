from django.urls import reverse

from api.data.models import Gallery, Widget
from lib.utils import with_camel_keys


def galleries(request):
    return {
        'galleries': Gallery.objects.all(),
        'gallery_vars': with_camel_keys({
            'urls': {
                'update': reverse('api:galleries-update-many')
            }
        })
    }


def wallpapers(request):
    gallery = Gallery.objects.filter(active=True).first()
    return {
        'background_vars': with_camel_keys({
            'gallery': gallery.pk if gallery else None,
            'urls': {
                'list': reverse('api:backgrounds-list')
            }
        })
    }


def widgets(request):
    return {
        'widgets': Widget.objects.filter(is_enabled=True)
    }
