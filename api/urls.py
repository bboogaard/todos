from rest_framework import routers

from api.views.files import FileViewSet
from api.views.notes import NoteViewSet
from api.views.snippets import CodeSnippetViewSet
from api.views.todos import TodoViewSet
from api.views.upload import UploadViewSet


app_name = 'api'


router = routers.SimpleRouter(trailing_slash=False)
router.register(r'files', FileViewSet, 'files')
router.register(r'notes', NoteViewSet, 'notes')
router.register(r'snippets', CodeSnippetViewSet, 'snippets')
router.register(r'todos', TodoViewSet, 'todos')
router.register(r'upload', UploadViewSet, 'upload')
urlpatterns = router.urls
