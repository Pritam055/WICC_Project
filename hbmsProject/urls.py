
from django.contrib import admin
from django.urls import path, include 
from django.conf import settings 
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    path('', include('hotels.urls', namespace='hotels')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('stats/', include('stats.urls', namespace='stats')),

    path('api/hotels/', include('hotels.api.urls', namespace='hotels-api')),
    path('api/accounts/', include('accounts.api.urls', namespace='accounts-api')),
    
    
    
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# if settings.DEBUG:
#     import debug_toolbar
#     urlpatterns +=  path('__debug__/', include('debug_toolbar.urls')), 
 