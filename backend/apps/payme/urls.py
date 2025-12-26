from django.urls import path
from .views import (
    # Card views
    CardCreateView,
    CardGetVerifyCodeView,
    CardVerifyView,
    CardCheckView,
    CardRemoveView,
    CardListView,
    CardDetailView,
    # Receipt views
    ReceiptCreateView,
    ReceiptPayView,
    ReceiptListView,
    ReceiptDetailView,
    ReceiptCheckView,
    # Agent Box Balance views
    AgentBoxListView,
    AgentBoxBalanceTopUpView,
    AgentBoxBalanceView,
)

urlpatterns = [
    # Card endpoints
    path("cards/", CardListView.as_view(), name="payme-card-list"),
    path("cards/<int:pk>/", CardDetailView.as_view(), name="payme-card-detail"),
    path("cards/create/", CardCreateView.as_view(), name="payme-card-create"),
    path(
        "cards/get-verify-code/",
        CardGetVerifyCodeView.as_view(),
        name="payme-card-get-verify-code",
    ),
    path("cards/verify/", CardVerifyView.as_view(), name="payme-card-verify"),
    path("cards/check/", CardCheckView.as_view(), name="payme-card-check"),
    path("cards/remove/", CardRemoveView.as_view(), name="payme-card-remove"),
    # Receipt endpoints
    path("receipts/", ReceiptListView.as_view(), name="payme-receipt-list"),
    path(
        "receipts/<int:pk>/", ReceiptDetailView.as_view(), name="payme-receipt-detail"
    ),
    path("receipts/create/", ReceiptCreateView.as_view(), name="payme-receipt-create"),
    path("receipts/pay/", ReceiptPayView.as_view(), name="payme-receipt-pay"),
    path(
        "receipts/<int:pk>/check/",
        ReceiptCheckView.as_view(),
        name="payme-receipt-check",
    ),
    # Agent Box Balance endpoints
    path("agent/boxes/", AgentBoxListView.as_view(), name="agent-box-list"),
    path(
        "agent/boxes/<int:pk>/",
        AgentBoxBalanceView.as_view(),
        name="agent-box-balance-detail",
    ),
    path(
        "agent/boxes/topup/",
        AgentBoxBalanceTopUpView.as_view(),
        name="agent-box-balance-topup",
    ),
]
