from django.urls import path
from .views import GetAuthToken, UserListRegisterView, UserAdmninRetrieveView


urlpatterns = [
    path('api-token-auth/', GetAuthToken.as_view()),
    path('register/', UserListRegisterView.as_view()),
    
    path('admin_register/<int:pk>/', UserAdmninRetrieveView.as_view()),
]
