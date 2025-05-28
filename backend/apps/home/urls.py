from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

app_name = "home"

# Router for viewsets
router = DefaultRouter()
router.register(r"regions", views.RegionViewSet, basename="region")

urlpatterns = [
    # Router URLs for regions
    path("", include(router.urls)),
    # Main report endpoint - as requested
    path("report/", views.HomeReportView.as_view(), name="home-report"),
    # Home management
    path("homes/", views.HomeListCreateView.as_view(), name="home-list-create"),
    path("homes/<int:pk>/", views.HomeDetailView.as_view(), name="home-detail"),
    # Warning endpoints
    path("warning/", views.HomeWarningView.as_view(), name="home-warning"),
    path(
        "region-warnings/",
        views.RegionHomesWarningView.as_view(),
        name="region-warnings",
    ),
    # Membership management
    path("join/", views.JoinHomeView.as_view(), name="join-home"),
    path("leave/", views.LeaveHomeView.as_view(), name="leave-home"),
    path("members/", views.HomeMembersView.as_view(), name="home-members"),
    # Status check
    path("status/", views.my_home_status, name="home-status"),
]
