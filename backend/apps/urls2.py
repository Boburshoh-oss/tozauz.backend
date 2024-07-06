from django.urls import path, include
from apps.bank.statistics_view import DashboardView

# urls conf file for apps folder

urlpatterns = [
    path("ecopacket/", include("apps.ecopacket.urls2")),
    
]