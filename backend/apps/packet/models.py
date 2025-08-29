from django.db import models
from apps.utils import get_uid

# Create your models here.

class FilterType(models.TextChoices):
    # -aluminum
    # -plastic
    # -glass
    # //Package
    # -yellow
    # -black
    # -red
    ALUMINUM = "aluminum", "Aluminum"
    PLASTIC = "plastic", "Plastic"
    GLASS = "glass", "Glass"
    YELLOW = "yellow", "Yellow"
    BLACK = "black", "Black"
    RED = "red", "Red"


class Category(models.Model):
    name = models.CharField(max_length=50)
    summa = models.PositiveIntegerField()
    ignore_agent = models.BooleanField(default=False)
    filter_type = models.CharField(
        max_length=20,
        choices=FilterType.choices,
        default=FilterType.BLACK
    )

    def __str__(self) -> str:
        return self.name

    @property
    def count_user(self):
        return self.user.all().count()


class Packet(models.Model):
    category = models.ForeignKey(
        "packet.Category", on_delete=models.SET_NULL, null=True
    )
    qr_code = models.CharField(max_length=50, blank=True)
    employee = models.ForeignKey(
        to="account.User", on_delete=models.SET_NULL, blank=True, null=True
    )
    scannered_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self) -> str:
    #     return f"{self.id} {self.category.name}"
