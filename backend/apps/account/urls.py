from django.urls import path
from .views import (
    GetAuthToken,
    UserRegisterView,
    UserAdminRetrieveView,
    UserAdminRegisterView,
    AdminGetAuthToken,
    UserUpdateRetrieveView,
    UserChangePasswordView,
    UserDeleteView,
    UserDeleteByIdView,
)

from .views import (
    RegisterView,
    VerifyRegistrationOTPView,
    ForgotPasswordView,
    VerifyForgotPasswordOTPView,
    UserProfileUpdateView,
)


urlpatterns = [
    path("api-token-auth/", GetAuthToken.as_view()),
    path("register/", UserRegisterView.as_view()),
    path("admin-register/", UserAdminRegisterView.as_view()),
    path("admin-register/<int:pk>/", UserAdminRetrieveView.as_view()),
    path("user-update/<int:pk>/", UserUpdateRetrieveView.as_view()),
    path("user-update-password/", UserChangePasswordView.as_view()),
    path("user-delete/", UserDeleteView.as_view()),
    path("user-delete/<int:user_id>/", UserDeleteByIdView.as_view()),
    path("admin-login/", AdminGetAuthToken.as_view()),

]

urlpatterns2 = [
    path('register-otp/', RegisterView.as_view(), name='register'),
    path('verify-registration-otp/', VerifyRegistrationOTPView.as_view(), name='verify_registration_otp'),
    path('forgot-password/', ForgotPasswordView.as_view(), name='forgot_password'),
    path('verify-forgot-password-otp/', VerifyForgotPasswordOTPView.as_view(), name='verify_forgot_password_otp'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile-update'),
]

urlpatterns += urlpatterns2
