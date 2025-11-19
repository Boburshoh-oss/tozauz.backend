from django.db import models
from apps.utils import get_uid
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.


class Box(models.Model):
    name = models.CharField(max_length=200)
    sim_module = models.CharField(max_length=20, unique=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    datetime_of_delivery = models.DateTimeField(blank=True, null=True)
    unloading_price = models.PositiveBigIntegerField(default=0)
    fandomat = models.BooleanField(default=False)
    containers_count = models.PositiveIntegerField(default=0)
    qr_code = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    category = models.ForeignKey(
        "packet.Category", on_delete=models.SET_NULL, null=True
    )
    is_active = models.BooleanField(default=True)
    
    seller = models.ForeignKey(
        to="account.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="box",
    )
    seller_share = models.DecimalField(max_digits=20, decimal_places=2, default=0)
    seller_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
    )

    def __str__(self) -> str:
        return f"Box {self.sim_module}"

    @property
    def state(self):
        return self.lifecycle.last().state

    @property
    def cycle_created_at(self):
        return self.lifecycle.last().started_at

    def save(self, *args, **kwargs) -> None:
        self.qr_code = self.sim_module
        return super().save(*args, **kwargs)


class LifeCycle(models.Model):
    box = models.ForeignKey(Box, on_delete=models.CASCADE, related_name="lifecycle")
    location = models.CharField(blank=True, null=True, max_length=255)
    employee = models.ForeignKey(
        to="account.User", on_delete=models.SET_NULL, null=True, blank=True
    )
    state = models.PositiveSmallIntegerField(default=0)
    started_at = models.DateTimeField(auto_now_add=True)
    filled_at = models.DateTimeField(blank=True, null=True)

    def __str__(self) -> str:
        return f"{self.box.name} {self.employee}"


class EcoPacketQrCode(models.Model):
    qr_code = models.CharField(max_length=50)
    user = models.ForeignKey(
        to="account.User", on_delete=models.SET_NULL, blank=True, null=True
    )
    life_cycle = models.ForeignKey(
        to=LifeCycle, on_delete=models.SET_NULL, blank=True, null=True
    )
    category = models.ForeignKey(
        "packet.Category", on_delete=models.SET_NULL, null=True
    )
    scannered_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.qr_code

    @property
    def box(self):
        if self.life_cycle is not None:
            return self.life_cycle.box

        return None


class FlaskQrCode(models.Model):
    bar_code = models.CharField(max_length=50,unique=True)

    category = models.OneToOneField(
        "packet.Category", on_delete=models.SET_NULL, null=True, blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    image = models.ImageField(upload_to="flask_qr_codes/", blank=True, null=True)
    def __str__(self) -> str:
        return self.bar_code

