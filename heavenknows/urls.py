from django.contrib import admin
from django.urls import path, include


urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('accounts.urls')),
    path('business/', include('businesses.urls')),
    path('destinations/', include('destinations.urls')),
    path('packages/', include('packages.urls')),
    path('', include('explore.urls')),
]

from django.contrib import admin
admin.site.site_header = 'HeavenKnows Adminstration'                 # default: "Django Administration"
admin.site.index_title = 'HeavenKnows Adminstration'                 # default: "Site administration"
admin.site.site_title = 'HeavenKnows Adminstration'                  # default: "Django site admin"


from django.conf import settings
from django.conf.urls.static import static
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)