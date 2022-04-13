from rest_framework import routers

from api.views.todos import TodoViewSet


app_name = 'api'


router = routers.SimpleRouter()
router.register(r'todos', TodoViewSet, 'todos')
urlpatterns = router.urls
