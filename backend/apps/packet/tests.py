from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Category
from apps.ecopacket.models import Box, EcoPacketQrCode, LifeCycle
from apps.bank.models import BankAccount, Earning
import json

User = get_user_model()


class CategoryIgnoreAgentTestCase(TestCase):
    """Category modeli ignore_agent funksionalligini testlash"""

    def setUp(self):
        """Test ma'lumotlarini yaratish"""
        # Test kategoriyalar yaratish
        self.category_normal = Category.objects.create(
            name="Normal", summa=100, ignore_agent=False
        )
        self.category_ignored = Category.objects.create(
            name="Ignored", summa=100, ignore_agent=True
        )

        # Test foydalanuvchilar yaratish
        self.user = User.objects.create_user(
            phone_number="+998901234567",
            first_name="Test",
            last_name="User",
            password="testpass123",
        )
        self.seller = User.objects.create_user(
            phone_number="+998901234568",
            first_name="Test",
            last_name="Seller",
            password="testpass123",
            role="agent",
        )

        # Bank accountlar yaratish
        self.user_bank = BankAccount.objects.create(user=self.user, capital=0)
        self.seller_bank = BankAccount.objects.create(user=self.seller, capital=0)

        # Box yaratish
        self.box = Box.objects.create(
            name="Test Box",
            sim_module="TEST001",
            qr_code="TESTBOX001",
            seller=self.seller,
            seller_percentage=30.0,
        )

        # LifeCycle yaratish
        self.lifecycle = LifeCycle.objects.create(box=self.box, state=1)

        # QR kodlar yaratish
        self.qr_normal = EcoPacketQrCode.objects.create(
            qr_code="NORMAL001", category=self.category_normal
        )
        self.qr_ignored = EcoPacketQrCode.objects.create(
            qr_code="IGNORED001", category=self.category_ignored
        )

    def test_category_creation(self):
        """Kategoriyalar to'g'ri yaratilganligini tekshirish"""
        self.assertEqual(self.category_normal.name, "Normal")
        self.assertFalse(self.category_normal.ignore_agent)
        self.assertEqual(self.category_ignored.name, "Ignored")
        self.assertTrue(self.category_ignored.ignore_agent)

    def simulate_scan_packet(self, qr_code, user, box):
        """Paketni skanerlashni simulatsiya qilish"""
        from django.utils import timezone

        ecopacket_qr = EcoPacketQrCode.objects.get(qr_code=qr_code)
        last_lifecycle = box.lifecycle.last()

        ecopacket_qr.scannered_at = timezone.now()
        ecopacket_qr.life_cycle = last_lifecycle
        ecopacket_qr.user = user
        ecopacket_qr.save()

        ecopakcet_money = ecopacket_qr.category.summa
        ecopakcet_catergory = ecopacket_qr.category
        bank_account = user.bankaccount

        # Kategoriya ignore_agent=True bo'lsa, hamma pul foydalanuvchiga beriladi
        if ecopakcet_catergory.ignore_agent:
            # Seller ulushini hisoblamay, hammasi foydalanuvchiga boradi
            bank_account.capital += ecopakcet_money
            bank_account.save()

            # Foydalanuvchi uchun daromad yozib qo'yiladi
            Earning.objects.create(
                bank_account=bank_account,
                amount=ecopakcet_money,
                tarrif=ecopakcet_catergory.name,
                box=box,
            )
        else:
            # Agar ignore_agent=False bo'lsa, odatiy hisob-kitob
            seller_percentage = box.seller_percentage
            if box.seller is not None:
                # Seller ulushini hisoblash
                seller_share = ecopakcet_money * seller_percentage / 100
                client_share = ecopakcet_money - seller_share

                # Seller hisobiga o'tkazish
                bank_account_seller = box.seller.bankaccount
                bank_account_seller.capital += seller_share
                bank_account_seller.save()

                # Box da seller ulushini saqlash
                box.seller_share += seller_share
                box.save()

                # Client hisobiga client ulushini o'tkazish
                bank_account.capital += client_share
            else:
                # Seller bo'lmasa hamma summa clientga
                bank_account.capital += ecopakcet_money

            bank_account.save()

            # Client uchun daromad yozib qo'yiladi
            Earning.objects.create(
                bank_account=bank_account,
                amount=client_share if box.seller is not None else ecopakcet_money,
                tarrif=ecopakcet_catergory.name,
                box=box,
            )

        return {
            "user_balance": user.bankaccount.capital,
            "seller_balance": box.seller.bankaccount.capital if box.seller else 0,
            "box_seller_share": box.seller_share,
        }

    def test_normal_category_scan(self):
        """Normal kategoriya (ignore_agent=False) skanerlash testsi"""
        result = self.simulate_scan_packet(
            qr_code="NORMAL001", user=self.user, box=self.box
        )

        # Foydalanuvchiga summa - seller ulushi beriladi
        expected_user_amount = self.category_normal.summa * 0.7  # 70%
        expected_seller_amount = self.category_normal.summa * 0.3  # 30%

        self.assertEqual(result["user_balance"], expected_user_amount)
        self.assertEqual(result["seller_balance"], expected_seller_amount)
        self.assertEqual(result["box_seller_share"], expected_seller_amount)

    def test_ignored_category_scan(self):
        """Ignored kategoriya (ignore_agent=True) skanerlash testsi"""
        result = self.simulate_scan_packet(
            qr_code="IGNORED001", user=self.user, box=self.box
        )

        # Barcha summa foydalanuvchiga beriladi
        expected_user_amount = self.category_ignored.summa  # 100%
        expected_seller_amount = 0  # 0%

        self.assertEqual(result["user_balance"], expected_user_amount)
        self.assertEqual(result["seller_balance"], expected_seller_amount)
        self.assertEqual(result["box_seller_share"], 0)  # Box seller ulushi o'zgarmaydi
