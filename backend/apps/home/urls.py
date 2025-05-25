from django.urls import path
from . import views

app_name = "home"

urlpatterns = [
    # Main report endpoint - as requested
    path("report/", views.HomeReportView.as_view(), name="home-report"),
    # Home management
    path("homes/", views.HomeListCreateView.as_view(), name="home-list-create"),
    path("homes/<int:pk>/", views.HomeDetailView.as_view(), name="home-detail"),
    # Membership management
    path("join/", views.JoinHomeView.as_view(), name="join-home"),
    path("leave/", views.LeaveHomeView.as_view(), name="leave-home"),
    path("members/", views.HomeMembersView.as_view(), name="home-members"),
    # Status check
    path("status/", views.my_home_status, name="home-status"),
]
