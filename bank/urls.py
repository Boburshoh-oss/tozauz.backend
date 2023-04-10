from django.urls import path
# from rest_framework import routers
from .views import (BankAccountListAPIView,
                    EarningListAPIView,
                    EarningUserAPIView,
                    PayOutListCreateAPIView,
                    PayOutListAPIView,
                    MeBankAccountAPIView,
                    AdminBankAccountAPIView,
                    )
urlpatterns = [
    path('bank-accounts/', BankAccountListAPIView.as_view(),
         name='bank-accounts'),
    path('me-bank/', MeBankAccountAPIView.as_view()),
    path('admin-bank-account/<int:user_id>/', AdminBankAccountAPIView.as_view()),
    path('earning-list/<int:pk>/', EarningUserAPIView.as_view()),
    path('earning-list/', EarningListAPIView.as_view()),
    path('payout-list/<int:pk>/', PayOutListAPIView.as_view()),
    path('payout-list-create/', PayOutListCreateAPIView.as_view())
]
