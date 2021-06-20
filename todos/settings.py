from lib.settings import BaseCacheSettings, CharField, IntegerField
from todos import models


class CacheSettings(BaseCacheSettings):

    todos_provider = CharField(default='local')

    gallery = IntegerField()

    def load(self, **defaults):
        gallery = models.Gallery.objects.first()
        defaults['gallery'] = gallery.pk if gallery else None
        return super().load(**defaults)


cache_settings = CacheSettings('todos-settings')
