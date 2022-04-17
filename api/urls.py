from rest_framework import routers

from api.views.notes import NoteViewSet
from api.views.snippets import CodeSnippetViewSet
from api.views.todos import TodoViewSet


app_name = 'api'


router = routers.SimpleRouter(trailing_slash=False)
router.register(r'notes', NoteViewSet, 'notes')
router.register(r'snippets', CodeSnippetViewSet, 'snippets')
router.register(r'todos', TodoViewSet, 'todos')
urlpatterns = router.urls
