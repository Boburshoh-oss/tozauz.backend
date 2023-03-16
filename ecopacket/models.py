from django.contrib.gis.db import models
from utils import get_uid

# Create your models here.


class Box(models.Model):
    name = models.CharField(max_length=200)
    sim_module = models.CharField(max_length=20,unique=True)
    qr_code = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        "packet.Category", on_delete=models.SET_NULL, null=True)

    def __str__(self) -> str:
        return f'Box {self.sim_module}'


class LifeCycle(models.Model):
    box = models.ForeignKey(Box, on_delete=models.CASCADE,related_name="lifecycle")
    location = models.PointField(blank=True, null=True)
    employee = models.ForeignKey(
        to='account.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    state = models.PositiveSmallIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    filled_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.box.name} {self.employee}"


class EcoPacketQrCode(models.Model):
    qr_code = models.CharField(max_length=50)
    user = models.ForeignKey(
        to='account.User',
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    life_cycle = models.ForeignKey(
        to=LifeCycle,
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    category = models.ForeignKey(
        "packet.Category", on_delete=models.SET_NULL, null=True)
    scannered_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.qr_code
