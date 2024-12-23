from django.urls import path

# from rest_framework import routers
from .views import (
    BankAccountListAPIView,
    EarningListAPIView,
    EarningToPenaltyView,
    EarningUserAPIView,
    MobileEarningListAPIView,
    PayOutListCreateAPIView,
    PayOutListAPIView,
    MeBankAccountAPIView,
    AdminBankAccountAPIView,
    PayMeCreateAPIView,
    PayMeListAPIView,
    PayOutUserMobileListAPIView,
    PayMePayedView,
    AgentEarningListAPIView,
)

urlpatterns = [
    # bank account urls
    path("bank-accounts/", BankAccountListAPIView.as_view(), name="bank-accounts"),
    path("me-bank/", MeBankAccountAPIView.as_view()),
    path("admin-bank-account/<int:user_id>/", AdminBankAccountAPIView.as_view()),
    # earning urls
    path("earning-list/<int:pk>/", EarningUserAPIView.as_view()),
    path("earning-to-penalty/<int:pk>/", EarningToPenaltyView.as_view()),
    path("earning-list/", EarningListAPIView.as_view()),
    path("mobile-earning-list/", MobileEarningListAPIView.as_view()),
    # payout urls
    path("payout-list/<int:pk>/", PayOutListAPIView.as_view()),
    path("payout-list-create/", PayOutListCreateAPIView.as_view()),
    path("payout-list-user/", PayOutUserMobileListAPIView.as_view()),
    # payme urls
    path("payme-create/", PayMeCreateAPIView.as_view()),
    path("payme-list/", PayMeListAPIView.as_view()),
    path("payme-payed/<int:pk>/", PayMePayedView.as_view()),
    # agent urls
    path("agent-earning-list/", AgentEarningListAPIView.as_view()),
]
