from todos import models
from todos.settings import cache_settings


def settings(request):
    return {
        'settings': cache_settings.load()
    }


def wallpapers(request):
    gallery = cache_settings.load()['gallery'].value
    if gallery:
        wallpaper_images = [
            wallpaper.get_image_url()
            for wallpaper in models.Wallpaper.objects.filter(gallery=gallery)
        ]
    else:
        wallpaper_images = []
    return {
        'galleries': list(models.Gallery.objects.values_list('id', 'name')),
        'wallpapers': wallpaper_images
    }
