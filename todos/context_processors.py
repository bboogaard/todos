from constance import config

from todos import models


def wallpapers(request):
    gallery = config.gallery
    if gallery:
        wallpaper_images = [
            wallpaper.get_image_url()
            for wallpaper in models.Wallpaper.objects.filter(gallery=gallery)
        ]
    else:
        wallpaper_images = []
    return {
        'galleries': list(models.Gallery.objects.with_images().values_list('id', 'name')),
        'wallpapers': wallpaper_images
    }
