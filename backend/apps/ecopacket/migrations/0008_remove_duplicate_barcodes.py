# Generated manually to fix duplicate bar_codes
from django.db import migrations


def remove_duplicate_barcodes(apps, schema_editor):
    """
    Dublikat bar_code'larni o'chirish.
    Har bir bar_code uchun faqat birinchi yozuvni saqlab, qolganlarini o'chirish.
    """
    FlaskQrCode = apps.get_model("ecopacket", "FlaskQrCode")

    # Barcha bar_code'larni olish
    seen = {}
    to_delete = []

    for obj in FlaskQrCode.objects.all().order_by("id"):
        if obj.bar_code in seen:
            # Bu bar_code allaqachon ko'rilgan, demak bu dublikat
            to_delete.append(obj.id)
        else:
            # Birinchi marta ko'rilgan bar_code, uni saqlaymiz
            seen[obj.bar_code] = obj.id

    # Dublikatlarni o'chirish (faqat birinchi yozuvdan tashqari)
    if to_delete:
        FlaskQrCode.objects.filter(id__in=to_delete).delete()
        print(
            f"Deleted {len(to_delete)} duplicate bar_codes, kept {len(seen)} unique bar_codes"
        )


class Migration(migrations.Migration):

    dependencies = [
        ("ecopacket", "0007_remove_flaskqrcode_scannered_at_and_more"),
    ]

    operations = [
        migrations.RunPython(
            remove_duplicate_barcodes, reverse_code=migrations.RunPython.noop
        ),
    ]
