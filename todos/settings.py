from lib.settings import BaseCacheSettings, CharField, IntegerField
from todos import models


class CacheSettings(BaseCacheSettings):

    todos_provider = CharField(default='local')

    gallery = IntegerField()

    notes_provider = CharField(default='local')

    odd_weeks_background = CharField(default='')

    odd_weeks_color = CharField(default='')

    even_weeks_background = CharField(default='')

    even_weeks_color = CharField(default='')

    def load(self, **defaults):
        gallery = models.Gallery.objects.with_images().first()
        defaults['gallery'] = gallery.pk if gallery else None
        return super().load(**defaults)


cache_settings = CacheSettings('todos-settings')
