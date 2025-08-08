from django.urls import path, include
from apps.bank.statistics_view import DashboardView

# urls conf file for apps folder

urlpatterns = [
    path("account/", include("apps.account.urls")),
    path("ecopacket/", include("apps.ecopacket.urls.urls")),
    path("ecopacket/", include("apps.ecopacket.urls.urls2")),
    path("ecopacket/flask-qr/", include("apps.ecopacket.urls.flask_qr")),
    path("packet/", include("apps.packet.urls")),
    path("bank/", include("apps.bank.urls")),
    path("home/", include("apps.home.urls")),
    path("dashboard/", DashboardView.as_view()),
]
