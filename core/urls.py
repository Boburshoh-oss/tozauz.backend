from django.conf import settings
from django.conf.urls.static import static
from .yasg import swaggerurlpatterns
from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView

urlpatterns = [
    path('__debug__/', include('debug_toolbar.urls')),
    path('admin/', admin.site.urls),

    path('api/v1/account/', include('account.urls')),
    path('api/v1/ecopacket/', include('ecopacket.urls')),
    path('api/v1/packet/', include('packet.urls')),
    path('api/v1/bank/', include('bank.urls')),
    re_path(r'^(?!\/api\/).*', TemplateView.as_view(template_name='index.html')),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += swaggerurlpatterns
