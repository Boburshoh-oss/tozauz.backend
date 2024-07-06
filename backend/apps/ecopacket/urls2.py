from django.urls import path
from .views import (
    BoxLocationAPIViewV2
)

urlpatterns = [
    path("box-location/",BoxLocationAPIViewV2.as_view()),
]
