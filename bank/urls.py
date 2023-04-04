from django.urls import path
# from rest_framework import routers
from .views import (BankAccountListAPIView,
                    EarningListAPIView,
                    PayOutListCreateAPIView,
                    PayOutListAPIView,
                    MeBankAccountAPIView,
                    )
urlpatterns = [
    path('bank-accounts/', BankAccountListAPIView.as_view(),
         name='bank-accounts'),
    path('me-bank/', MeBankAccountAPIView.as_view()),
    path('earning-list/<int:pk>/', EarningListAPIView.as_view()),
    path('payout-list/<int:pk>/', PayOutListAPIView.as_view()),
    path('payout-list-create/', PayOutListCreateAPIView.as_view())
]
