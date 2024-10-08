# Generated by Django 4.1.7 on 2024-08-06 07:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='earning',
            name='is_penalty',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='earning',
            name='penalty_amount',
            field=models.PositiveBigIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='earning',
            name='reason',
            field=models.TextField(blank=True, default=''),
        ),
    ]
