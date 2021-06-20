from todos import models
from todos.settings import cache_settings


def settings(request):
    return {
        'settings': cache_settings.load()
    }


def wallpapers(request):
    return {
        'galleries': list(models.Gallery.objects.values_list('id', 'name')),
    }
