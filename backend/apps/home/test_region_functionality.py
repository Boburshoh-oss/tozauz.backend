"""
Hudud va oylik limit funksionalligini test qilish uchun script
"""

from django.test import TestCase
from django.utils import timezone
from django.contrib.auth import get_user_model
from apps.home.models import Region, Home, HomeMembership, WasteMonthlyReport
from apps.ecopacket.models import EcoPacketQrCode, LifeCycle, Box
from apps.packet.models import Category

User = get_user_model()


class RegionFunctionalityTestCase(TestCase):
    """Hudud funksionalligini test qilish"""

    def setUp(self):
        """Test ma'lumotlarini yaratish"""
        # Test kategoriya yaratish
        self.category = Category.objects.create(name="Plastik", summa=100)

        # Test hudud yaratish
        self.region = Region.objects.create(
            name="Test Hudud",
            code="TEST-01",
            monthly_waste_limit=15,
            description="Test hudud",
            is_active=True,
        )

        # Test foydalanuvchilar yaratish
        self.user1 = User.objects.create_user(
            phone_number="+998901234567",
            first_name="Test",
            last_name="User1",
            password="testpass123",
        )

        self.user2 = User.objects.create_user(
            phone_number="+998901234568",
            first_name="Test",
            last_name="User2",
            password="testpass123",
        )

        # Test uy yaratish
        self.home = Home.objects.create(
            name="Test Uy",
            region=self.region,
            address="Test manzil",
            description="Test uy",
            owner=self.user1,
        )

        # Uy a'zoligi yaratish
        HomeMembership.objects.create(home=self.home, user=self.user1, is_admin=True)

        HomeMembership.objects.create(home=self.home, user=self.user2, is_admin=False)

    def test_region_creation(self):
        """Hudud yaratish testsi"""
        self.assertEqual(self.region.name, "Test Hudud")
        self.assertEqual(self.region.code, "TEST-01")
        self.assertEqual(self.region.monthly_waste_limit, 15)
        self.assertTrue(self.region.is_active)

    def test_home_region_relationship(self):
        """Uy-hudud aloqasi testsi"""
        self.assertEqual(self.home.region, self.region)
        self.assertEqual(self.region.total_homes, 1)
        self.assertEqual(self.region.total_active_members, 2)

    def test_monthly_waste_statistics(self):
        """Oylik chiqindi statistikasi testsi"""
        # Hech qanday skan bo'lmagan holat
        stats = self.region.get_monthly_waste_statistics()
        self.assertEqual(stats["total_scans"], 0)
        self.assertEqual(stats["limit"], 15)
        self.assertEqual(stats["remaining"], 15)
        self.assertFalse(stats["is_exceeded"])
        self.assertEqual(stats["usage_percentage"], 0)

    def test_home_monthly_waste_count(self):
        """Uy oylik chiqindi soni testsi"""
        count = self.home.get_monthly_waste_count()
        self.assertEqual(count, 0)

    def test_region_warning_check(self):
        """Hudud ogohlantirish testsi"""
        warning_data = self.home.check_region_limit_warning()
        self.assertFalse(warning_data["has_warning"])
        self.assertFalse(warning_data["is_critical"])
        self.assertEqual(warning_data["home_contribution"], 0)

    def test_monthly_report_generation(self):
        """Oylik hisobot yaratish testsi"""
        now = timezone.now()
        report = WasteMonthlyReport.generate_monthly_report(
            self.region, now.year, now.month
        )

        self.assertEqual(report.region, self.region)
        self.assertEqual(report.year, now.year)
        self.assertEqual(report.month, now.month)
        self.assertEqual(report.total_scans, 0)
        self.assertEqual(report.total_homes, 1)
        self.assertEqual(report.total_members, 2)
        self.assertFalse(report.limit_exceeded)

    def test_warning_messages(self):
        """Ogohlantirish xabarlari testsi"""
        # Normal holat
        warning_data = self.home.check_region_limit_warning()
        self.assertEqual(warning_data["warning_message"], "")

    def tearDown(self):
        """Test ma'lumotlarini tozalash"""
        # Cleanup operations if needed
        pass


def create_test_data():
    """Manual test ma'lumotlarini yaratish uchun funksiya"""
    print("Test ma'lumotlarini yaratish boshlandi...")

    # Test kategoriya
    category, created = Category.objects.get_or_create(
        name="Plastik", defaults={"summa": 100}
    )
    if created:
        print("✓ Test kategoriya yaratildi: Plastik")

    # Test hudud
    region, created = Region.objects.get_or_create(
        code="TEST-01",
        defaults={
            "name": "Test Hudud",
            "monthly_waste_limit": 5,  # Test uchun kichik limit
            "description": "Bu test hududi",
            "is_active": True,
        },
    )
    if created:
        print("✓ Test hudud yaratildi: Test Hudud")

    # Test foydalanuvchi
    user, created = User.objects.get_or_create(
        phone_number="+998901111111",
        defaults={
            "first_name": "Test",
            "last_name": "Foydalanuvchi",
            "password": "testpass123",
        },
    )
    if created:
        print("✓ Test foydalanuvchi yaratildi: +998901111111")

    # Test uy
    home, created = Home.objects.get_or_create(
        name="Test Uy",
        defaults={
            "region": region,
            "address": "Test manzil, 123",
            "description": "Test uy",
            "owner": user,
        },
    )
    if created:
        print("✓ Test uy yaratildi: Test Uy")

    # Uy a'zoligi
    membership, created = HomeMembership.objects.get_or_create(
        user=user, defaults={"home": home, "is_admin": True}
    )
    if created:
        print("✓ Test a'zolik yaratildi")

    print("\n📊 Joriy statistika:")
    stats = region.get_monthly_waste_statistics()
    print(f"• Hudud: {region.name}")
    print(f"• Limit: {stats['limit']} ta paket/oy")
    print(f"• Joriy skanlar: {stats['total_scans']} ta")
    print(f"• Qolgan: {stats['remaining']} ta")
    print(f"• Foiz: {stats['usage_percentage']}%")

    warning_data = home.check_region_limit_warning()
    if warning_data["warning_message"]:
        print(f"• Ogohlantirish: {warning_data['warning_message']}")
    else:
        print("• ✅ Hech qanday ogohlantirish yo'q")

    print(
        f"\nTest ma'lumotlari tayyor! Limit testlash uchun {stats['limit']} dan ortiq paket skanerlang."
    )
    return {"region": region, "home": home, "user": user, "category": category}


if __name__ == "__main__":
    # Django setup
    import os
    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.development")
    django.setup()

    # Test ma'lumotlarini yaratish
    test_data = create_test_data()
