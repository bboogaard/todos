from todos.settings import cache_settings


def settings(request):
    return {
        'settings': cache_settings.load()
    }
