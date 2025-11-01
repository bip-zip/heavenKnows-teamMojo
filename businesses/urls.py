from django.urls import path
from . import views

app_name = 'businesses'

urlpatterns = [
    path('register/', views.BusinessRegisterView.as_view(), name='register'),
    path('dashboard/', views.BusinessDashboardView.as_view(), name='dashboard'),
     path('local-to-global/', views.LocalToGlobalView.as_view(), name='local_to_global'),
      path('accommodation/update/', views.AccommodationDetailsUpdateView.as_view(), name='update_accommodation'),
    path('manufacturer/update/', views.ManufacturerDetailsUpdateView.as_view(), name='update_manufacturer'),
    path('images/upload/', views.BusinessImageUploadView.as_view(), name='upload_image'),
    path('images/<int:pk>/delete/', views.BusinessImageDeleteView.as_view(), name='delete_image'),
]
