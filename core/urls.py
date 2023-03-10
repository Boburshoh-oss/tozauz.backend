from django.conf import settings
from django.conf.urls.static import static

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('admin/', admin.site.urls),

    path('api/v1/account/', include('account.urls')),
    path('api/v1/ecopacket/', include('ecopacket.urls')),
    path('api/v1/packet/', include('packet.urls')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
