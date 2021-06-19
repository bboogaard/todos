from django.urls import path

from . import views

app_name = 'todos'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('todos-save.json', views.TodosSaveJson.as_view(), name='todos_save.json'),
]
