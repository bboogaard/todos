from lib.settings import BaseCacheSettings, BooleanField, CharField, IntegerField
from todos import models


class CacheSettings(BaseCacheSettings):

    todos_provider = CharField(default='local')

    todos_position = CharField(default='top')

    gallery = IntegerField()

    show_files = BooleanField(default=False)

    show_notes = BooleanField(default=False)

    notes_provider = CharField(default='local')

    def load(self, **defaults):
        gallery = models.Gallery.objects.with_images().first()
        defaults['gallery'] = gallery.pk if gallery else None
        return super().load(**defaults)


cache_settings = CacheSettings('todos-settings')
