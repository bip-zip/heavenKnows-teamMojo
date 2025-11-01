from django.urls import path
from . import views

app_name = 'packages'

urlpatterns = [
    path('', views.PackageListView.as_view(), name='list'),
    path('create/', views.PackageCreateView.as_view(), name='create'),
    path('<slug:slug>/', views.PackageDetailView.as_view(), name='detail'),
    path('<slug:slug>/review/', views.PackageReviewCreateView.as_view(), name='add_review'),
    path('<slug:slug>/book/', views.PackageBookingCreateView.as_view(), name='book'),
    path('booking/<str:booking_number>/confirmation/', views.BookingConfirmationView.as_view(), name='booking_confirmation'),
]