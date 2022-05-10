from django.urls import path

from . import views

app_name = 'todos'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('cron/<job_name>', views.CronView.as_view(), name='cron'),
    path('search/', views.SearchView.as_view(), name='search'),

    # Images
    path('carousel', views.CarouselView.as_view(), name="carousel"),
]
