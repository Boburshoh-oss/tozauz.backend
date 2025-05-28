from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from .models import Home, HomeMembership
from apps.ecopacket.models import EcoPacketQrCode
from apps.packet.models import Category

User = get_user_model()


class HomeModelTest(TestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            phone_number="998901234567", first_name="Test", last_name="User1"
        )
        self.user2 = User.objects.create_user(
            phone_number="998901234568", first_name="Test", last_name="User2"
        )

    def test_home_creation(self):
        """Test Home model creation and invitation code generation"""
        home = Home.objects.create(
            name="Test Home", address="Test Address", owner=self.user1
        )

        self.assertTrue(home.invitation_code)
        self.assertEqual(len(home.invitation_code), 8)
        self.assertEqual(home.member_count, 0)  # No members yet
        self.assertEqual(home.total_ecopackets, 0)

    def test_home_membership_creation(self):
        """Test HomeMembership creation"""
        home = Home.objects.create(name="Test Home", owner=self.user1)
        membership = HomeMembership.objects.create(
            home=home, user=self.user1, is_admin=True
        )

        self.assertEqual(membership.home, home)
        self.assertEqual(membership.user, self.user1)
        self.assertTrue(membership.is_admin)
        self.assertEqual(home.member_count, 1)

    def test_user_home_property(self):
        """Test User.home property"""
        home = Home.objects.create(name="Test Home", owner=self.user1)

        # User without membership
        self.assertIsNone(self.user1.home)

        # User with membership
        HomeMembership.objects.create(home=home, user=self.user1)
        # Need to refresh from db
        self.user1.refresh_from_db()
        self.assertEqual(self.user1.home, home)


class HomeAPITest(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            phone_number="998901234567", first_name="Test", last_name="User1"
        )
        self.user2 = User.objects.create_user(
            phone_number="998901234568", first_name="Test", last_name="User2"
        )

        # Create test category for ecopackets
        self.category = Category.objects.create(name="Test Category", summa=100)

        self.home = Home.objects.create(
            name="Test Home", address="Test Address", owner=self.user1
        )

        # Create memberships
        self.membership1 = HomeMembership.objects.create(
            home=self.home, user=self.user1, is_admin=True
        )
        self.membership2 = HomeMembership.objects.create(
            home=self.home, user=self.user2, is_admin=False
        )

    def test_home_report_view_authenticated(self):
        """Test GET /api/home/report/ with authenticated user"""
        self.client.force_authenticate(user=self.user1)

        # Create some ecopackets for users
        EcoPacketQrCode.objects.create(
            qr_code="QR001", user=self.user1, category=self.category
        )
        EcoPacketQrCode.objects.create(
            qr_code="QR002", user=self.user1, category=self.category
        )
        EcoPacketQrCode.objects.create(
            qr_code="QR003", user=self.user2, category=self.category
        )

        url = reverse("home:home-report")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertEqual(data["home_id"], self.home.id)
        self.assertEqual(data["home_name"], self.home.name)
        self.assertEqual(data["member_count"], 2)
        self.assertEqual(data["total_ecopackets"], 3)
        self.assertEqual(len(data["members"]), 2)

        # Check member data
        member_data = {member["user_id"]: member for member in data["members"]}
        self.assertEqual(member_data[self.user1.id]["ecopacket_count"], 2)
        self.assertEqual(member_data[self.user2.id]["ecopacket_count"], 1)

    def test_home_report_view_unauthenticated(self):
        """Test GET /api/home/report/ without authentication"""
        url = reverse("home:home-report")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_home_report_view_no_home(self):
        """Test GET /api/home/report/ for user without home"""
        user3 = User.objects.create_user(
            phone_number="998901234569", first_name="Test", last_name="User3"
        )
        self.client.force_authenticate(user=user3)

        url = reverse("home:home-report")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertIn("Siz hech qanday uyga a'zo emassiz", response.data["error"])

    def test_create_home(self):
        """Test POST /api/home/homes/ - Create new home"""
        user3 = User.objects.create_user(
            phone_number="998901234569", first_name="Test", last_name="User3"
        )
        self.client.force_authenticate(user=user3)

        url = reverse("home:home-list-create")
        data = {
            "name": "New Test Home",
            "address": "New Address",
            "description": "Test description",
        }
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Check if home was created
        new_home = Home.objects.get(name="New Test Home")
        self.assertEqual(new_home.owner, user3)

        # Check if membership was created
        membership = HomeMembership.objects.get(user=user3, home=new_home)
        self.assertTrue(membership.is_admin)

    def test_join_home(self):
        """Test POST /api/home/join/ - Join home with invitation code"""
        user3 = User.objects.create_user(
            phone_number="998901234569", first_name="Test", last_name="User3"
        )
        self.client.force_authenticate(user=user3)

        url = reverse("home:join-home")
        data = {"invitation_code": self.home.invitation_code}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn("muvaffaqiyatli qo'shildingiz", response.data["message"])

        # Check if membership was created
        membership = HomeMembership.objects.get(user=user3, home=self.home)
        self.assertFalse(membership.is_admin)  # New members are not admin by default

    def test_join_home_invalid_code(self):
        """Test POST /api/home/join/ with invalid invitation code"""
        user3 = User.objects.create_user(
            phone_number="998901234569", first_name="Test", last_name="User3"
        )
        self.client.force_authenticate(user=user3)

        url = reverse("home:join-home")
        data = {"invitation_code": "INVALID123"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_join_home_already_member(self):
        """Test POST /api/home/join/ when user is already a member"""
        self.client.force_authenticate(user=self.user1)

        url = reverse("home:join-home")
        data = {"invitation_code": self.home.invitation_code}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_home_status(self):
        """Test GET /api/home/status/"""
        self.client.force_authenticate(user=self.user1)

        # Create some ecopackets
        EcoPacketQrCode.objects.create(
            qr_code="QR001", user=self.user1, category=self.category
        )

        url = reverse("home:home-status")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertTrue(data["has_home"])
        self.assertEqual(data["home_id"], self.home.id)
        self.assertEqual(data["home_name"], self.home.name)
        self.assertTrue(data["is_admin"])
        self.assertEqual(data["my_ecopacket_count"], 1)
        self.assertEqual(data["invitation_code"], self.home.invitation_code)

    def test_home_status_no_home(self):
        """Test GET /api/home/status/ for user without home"""
        user3 = User.objects.create_user(
            phone_number="998901234569", first_name="Test", last_name="User3"
        )
        self.client.force_authenticate(user=user3)

        url = reverse("home:home-status")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        self.assertFalse(data["has_home"])
        self.assertEqual(data["my_ecopacket_count"], 0)

    def test_leave_home(self):
        """Test POST /api/home/leave/"""
        self.client.force_authenticate(user=self.user2)  # Non-admin user

        url = reverse("home:leave-home")
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("muvaffaqiyatli chiqdingiz", response.data["message"])

        # Check membership was deleted
        self.assertFalse(HomeMembership.objects.filter(user=self.user2).exists())

    def test_leave_home_only_admin(self):
        """Test POST /api/home/leave/ when user is the only admin"""
        # Remove user2 to make user1 the only admin
        self.membership2.delete()

        self.client.force_authenticate(user=self.user1)

        url = reverse("home:leave-home")
        response = self.client.post(url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("yagona adminisiz", response.data["error"])
