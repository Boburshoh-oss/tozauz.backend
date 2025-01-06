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
    ApplicationCreateView,
    AgentApplicationListAPIView,
    AgentApplicationUpdateAPIView,
    AgentPayMeCreateView,
    AgentPayMeListView,
    AgentPayOutListView,
    AgentAdminApplicationListAPIView,
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
    path("agent-application-create/", ApplicationCreateView.as_view()),
    path("agent-application-list/", AgentApplicationListAPIView.as_view()),
    path("agent-application-update/<int:pk>/", AgentApplicationUpdateAPIView.as_view()),
    
    # agent payme urls
    path("agent/payme/create/", AgentPayMeCreateView.as_view(), name="agent-payme-create"),
    path("agent/payme/list/", AgentPayMeListView.as_view(), name="agent-payme-list"),
    # agent payout urls
    path("agent/payout/list/", AgentPayOutListView.as_view(), name="agent-payout-list"),
    # agent admin application list
    path("agent/admin/application/list/", AgentAdminApplicationListAPIView.as_view()),
]
