from django.urls import path

from . import views

app_name = 'todos'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('todos-save.json', views.TodosSaveJson.as_view(), name='todos_save.json'),
    path('todos-activate.json', views.TodosActivateJson.as_view(), name='todos_activate.json'),
    path('settings-save', views.SettingsSave.as_view(), name='settings_save'),
]
