from django.urls import path
# from rest_framework import routers
from .views import (BankAccountListAPIView,
                    EarningListAPIView,
                    PayOutListCreateAPIView
                    )
urlpatterns = [
    path('bank-accounts/', BankAccountListAPIView.as_view(),
         name='bank-accounts'),
    path('earning-list/', EarningListAPIView.as_view()),
    path('payout-list-create/', PayOutListCreateAPIView.as_view())
]
