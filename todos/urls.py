from django.urls import path

from . import views

app_name = 'todos'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('cron/<job_name>', views.CronView.as_view(), name='cron'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('notes-export', views.NotesExportView.as_view(), name='notes_export'),
    path('notes-import', views.NotesImportView.as_view(), name='notes_import'),
    path('snippets-export', views.CodeSnippetsExportView.as_view(), name='snippets_export'),
    path('snippets-import', views.CodeSnippetsImportView.as_view(), name='snippets_import'),

    # Wallpapers
    path('wallpapers/list', views.WallpaperListView.as_view(), name="wallpaper_list"),
    path('wallpapers/create', views.WallpaperCreateView.as_view(), name="wallpaper_create"),
    path('wallpapers/<int:pk>/update', views.WallpaperUpdateView.as_view(), name="wallpaper_update"),
    path('wallpapers/delete', views.WallpaperDeleteView.as_view(), name="wallpaper_delete"),

    # Images
    path('carousel', views.CarouselView.as_view(), name="carousel"),

    # Widgets
    path('widgets/list', views.WidgetListView.as_view(), name="widget_list"),
    path('widgets/<int:widget_id>', views.WidgetJson.as_view(), name="widget.json"),
]
