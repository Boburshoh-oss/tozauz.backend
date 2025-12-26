from django.conf import settings
from django.conf.urls.static import static
from .yasg import swaggerurlpatterns
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.urls")),
    path("api/v2/", include("apps.urls2")),
] + swaggerurlpatterns

# Debug toolbar faqat DEBUG rejimida
if settings.DEBUG:
    urlpatterns.append(path("__debug__/", include("debug_toolbar.urls")))

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# urlpatterns.append(re_path(r'^(?!\/api\/).*', TemplateView.as_view(template_name='index.html')))
