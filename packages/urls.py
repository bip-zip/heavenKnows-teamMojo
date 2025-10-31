from django.urls import path
from . import views

app_name = 'packages'

urlpatterns = [
     path('', views.PackageListView.as_view(), name='list'),
    path('create/', views.PackageCreateView.as_view(), name='create'),
    
]