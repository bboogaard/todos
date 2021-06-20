from lib.settings import BaseCacheSettings, CharField


class CacheSettings(BaseCacheSettings):

    todos_provider = CharField(default='local')


cache_settings = CacheSettings('todos-settings')
