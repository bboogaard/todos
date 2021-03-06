from rest_framework import routers

from api.views.events import EventViewSet
from api.views.files import FileViewSet
from api.views.galleries import GalleryViewSet
from api.views.images import CarouselViewSet, ImageViewSet
from api.views.notes import NoteViewSet
from api.views.snippets import CodeSnippetViewSet
from api.views.todos import TodoViewSet
from api.views.upload import UploadViewSet
from api.views.wallpapers import BackgroundViewSet, WallpaperViewSet
from api.views.widgets import WidgetViewSet


app_name = 'api'


router = routers.SimpleRouter(trailing_slash=False)
router.register(r'backgrounds', BackgroundViewSet, 'backgrounds')
router.register(r'events', EventViewSet, 'events')
router.register(r'files', FileViewSet, 'files')
router.register(r'galleries', GalleryViewSet, 'galleries')
router.register(r'images', ImageViewSet, 'images')
router.register(r'carousel', CarouselViewSet, 'carousel')
router.register(r'notes', NoteViewSet, 'notes')
router.register(r'snippets', CodeSnippetViewSet, 'snippets')
router.register(r'todos', TodoViewSet, 'todos')
router.register(r'upload', UploadViewSet, 'upload')
router.register(r'wallpapers', WallpaperViewSet, 'wallpapers')
router.register(r'widgets', WidgetViewSet, 'widgets')
urlpatterns = router.urls
