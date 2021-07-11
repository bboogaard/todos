from django.urls import path

from . import views

app_name = 'todos'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('todos-save.json', views.TodosSaveJson.as_view(), name='todos_save.json'),
    path('todos-activate.json', views.TodosActivateJson.as_view(), name='todos_activate.json'),
    path('settings-save', views.SettingsSave.as_view(), name='settings_save'),

    # Wallpapers
    path('wallpapers/list', views.WallpaperListView.as_view(), name="wallpaper_list"),
    path('wallpapers/create', views.WallpaperCreateView.as_view(), name="wallpaper_create"),
    path('wallpapers/<int:pk>/update', views.WallpaperUpdateView.as_view(), name="wallpaper_update"),
    path('wallpapers/delete', views.WallpaperDeleteView.as_view(), name="wallpaper_delete"),
]
