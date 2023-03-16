from django.urls import path
from .views import GetAuthToken, UserRegisterView, UserAdmninRetrieveView, UserAdminRegisterView, AdminGetAuthToken


urlpatterns = [
    path('api-token-auth/', GetAuthToken.as_view()),
    path('register/', UserRegisterView.as_view()),
    path('admin-register/', UserAdminRegisterView.as_view()),
    path('admin-register/<int:pk>/', UserAdmninRetrieveView.as_view()),
    path('admin-login/', AdminGetAuthToken.as_view())
]
