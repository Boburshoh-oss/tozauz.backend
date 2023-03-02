from django.contrib.gis.db import models
import uuid


class Category(models.Model):
    name = models.CharField(max_length=200)
    tarrif_amount = models.PositiveBigIntegerField()

    def __str__(self):
        return self.name


class Box(models.Model):
    name = models.CharField(max_length=50)
    category = models.ForeignKey(
        "garbage.Category", on_delete=models.SET_NULL, null=True)
    qr_code = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    sim_module = models.CharField(max_length=20)

    def __str__(self):
        return self.name


class BoxFillCycle(models.Model):
    box = models.ForeignKey("garbage.Box", on_delete=models.CASCADE)
    start_date = models.DateTimeField(auto_now_add=True)
    fill_date = models.DateTimeField(blank=True, null=True)
    state = models.IntegerField(default=0)
    location = models.PointField()

    def __str__(self) -> str:
        return f"{self.box.name} {self.start_date}"

