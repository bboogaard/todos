from app.settings import *


MEDIA_ROOT = os.path.join(BASE_DIR,'media/test')
PRIVATE_STORAGE_ROOT = os.path.join(BASE_DIR,'media/test/private')

# Search
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.whoosh_backend.WhooshEngine',
        'PATH': os.path.join(BASE_DIR, 'whoosh_index/test'),
    },
}
