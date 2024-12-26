from django.urls import path
from apps.ecopacket.views import (
    BoxLocationAPIViewV2,
    AgentBoxRetrieveView
)

urlpatterns = [
    path("box-location/",BoxLocationAPIViewV2.as_view()),
    path('boxes/<int:pk>/', AgentBoxRetrieveView.as_view(), name='agent-box-detail'),
]
