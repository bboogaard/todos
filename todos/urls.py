from django.urls import path

from . import views

app_name = 'todos'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('cron/<job_name>', views.CronView.as_view(), name='cron'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('todos-export', views.TodosExportView.as_view(), name='todos_export'),
    path('todos-import', views.TodosImportView.as_view(), name='todos_import'),
    path('notes-export', views.NotesExportView.as_view(), name='notes_export'),
    path('notes-import', views.NotesImportView.as_view(), name='notes_import'),

    # Wallpapers
    path('wallpapers/list', views.WallpaperListView.as_view(), name="wallpaper_list"),
    path('wallpapers/create', views.WallpaperCreateView.as_view(), name="wallpaper_create"),
    path('wallpapers/<int:pk>/update', views.WallpaperUpdateView.as_view(), name="wallpaper_update"),
    path('wallpapers/delete', views.WallpaperDeleteView.as_view(), name="wallpaper_delete"),

    # Files
    path('files/<file_type>/<int:pk>/delete.json', views.FileDeleteJson.as_view(), name="file_delete.json"),
    path('files/<file_type>/export', views.FileExportView.as_view(), name="file_export"),
    path('files/<file_type>/import', views.FileImportView.as_view(), name="file_import"),
    path('files/upload', views.FileUploadJson.as_view(), name="file_upload.json"),

    # Images
    path('carousel', views.CarouselView.as_view(), name="carousel"),

    # Widgets
    path('widgets/list', views.WidgetListView.as_view(), name="widget_list"),
    path('widgets/<int:widget_id>', views.WidgetJson.as_view(), name="widget.json"),

    # Events
    path('events/create', views.EventCreateView.as_view(), name="event_create"),
    path('events/<int:pk>/update', views.EventUpdateView.as_view(), name="event_update"),
    path('events/<int:pk>/delete', views.EventDeleteView.as_view(), name="event_delete"),

    # Dates
    path('dates/list', views.DateListView.as_view(), name="date_list"),
    path('dates/create', views.DateCreateView.as_view(), name="date_create"),
    path('dates/<int:pk>/update', views.DateUpdateView.as_view(), name="date_update"),
    path('dates/delete', views.DateDeleteView.as_view(), name="date_delete"),
]
