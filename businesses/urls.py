from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('register/', views.BusinessRegisterView.as_view(), name='register'),
    path('dashboard/', views.BusinessDashboardView.as_view(), name='dashboard'),
]
