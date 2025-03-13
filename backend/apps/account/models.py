
from datetime import datetime, timedelta
from django.utils import timezone
import random
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models

class RoleOptions(models.TextChoices):
    EMPLOYE = "EMP", "Employer"
    POPULATION = 'POP', 'Population'
    ADMIN = 'ADMIN', 'Admin'
    AGENT = 'AGENT', 'Agent'

class UserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, first_name=None, last_name=None, role=None, categories=None, car_number=None):
        if not phone_number:
            raise ValueError('Users must have a phone number')

        user = self.model(
            phone_number=phone_number,
            first_name=first_name,
            last_name=last_name,
            role=role,
            car_number=car_number
        )

        user.set_password(password)
        user.save(using=self._db)

        if categories:
            user.categories.set(categories)
        return user

    def create_superuser(self, phone_number, password, first_name=None, last_name=None, categories=None):
        user = self.create_user(
            phone_number=phone_number,
            password=password,
            first_name=first_name,
            last_name=last_name,
            role=RoleOptions.ADMIN,
            categories=categories,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user



class User(AbstractBaseUser):
    phone_number = models.CharField(max_length=20, unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    role = models.CharField(max_length=50, choices=RoleOptions.choices,
                            blank=True, null=True)
    categories = models.ManyToManyField("packet.Category", related_name="user", blank=True)
    car_number = models.CharField(max_length=10, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    inn = models.CharField(max_length=10, blank=True, null=True)
    bank_receipt = models.CharField(max_length=10, blank=True, null=True)
    
    # Add new OTP fields
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_created_at = models.DateTimeField(blank=True, null=True)
    objects = UserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['first_name']

    def __str__(self):
        return self.phone_number

    def get_full_name(self):
        return f"{self.first_name} {self.last_name}"

    def get_short_name(self):
        return self.first_name

    def has_perm(self, perm, obj=None):
        return True

    def has_module_perms(self, app_label):
        return True
    
    def generate_otp(self):
        """Generate a 6-digit OTP and save it to the user model"""
        otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
        self.otp = otp
        self.otp_created_at = timezone.now()
        self.save()
        return otp
    
    def verify_otp(self, otp):
        """Verify if the provided OTP matches and is not expired"""
        # Check if OTP is expired (5 minutes)
        if not self.otp_created_at:
            return False
            
        expiration_time = self.otp_created_at + timedelta(minutes=5)
        if timezone.now() > expiration_time:
            return False
            
        # Check if OTP matches
        return self.otp == otp
    
    def clear_otp(self):
        """Clear the OTP after successful verification"""
        self.otp = None
        self.otp_created_at = None
        self.save()

    @property
    def is_staff(self):
        return self.is_admin

    def save(self, *args, **kwargs):
        if self.role == RoleOptions.ADMIN:
            self.is_admin = True
        elif self.role == RoleOptions.POPULATION:
            self.is_admin = False
        elif self.role == RoleOptions.EMPLOYE:
            self.is_admin = False
        elif self.role == RoleOptions.AGENT:
            self.is_admin = False
            
        super(User, self).save(*args, **kwargs)
        
class AppVersion(models.Model):
    version = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.version

