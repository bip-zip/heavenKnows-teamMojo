from django.urls import path
from . import views

app_name = 'explore'

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
]
