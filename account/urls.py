from django.urls import path
from .views import (
    GetAuthToken,
    UserRegisterView,
    UserAdminRetrieveView,
    UserAdminRegisterView,
    AdminGetAuthToken,
    UserUpdateRetrieveView,
    UserChangePasswordView,
)


urlpatterns = [
    path("api-token-auth/", GetAuthToken.as_view()),
    path("register/", UserRegisterView.as_view()),
    path("admin-register/", UserAdminRegisterView.as_view()),
    path("admin-register/<int:pk>/", UserAdminRetrieveView.as_view()),
    path("user-update/<int:pk>/", UserUpdateRetrieveView.as_view()),
    path("user-update-password/", UserChangePasswordView.as_view()),
    path("admin-login/", AdminGetAuthToken.as_view()),
]
