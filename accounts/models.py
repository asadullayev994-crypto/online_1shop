import random
from datetime import timedelta
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    def create_user(self, email=None, phone_number=None, password=None, **extra_fields):
        if not email and not phone_number:
            raise ValueError(_("Email yoki Telefon raqam kiritilishi shart!"))
        if email:
            email = self.normalize_email(email)
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_verified', True)
        return self.create_user(email=email, password=password, **extra_fields)

class CustomUser(AbstractUser):
    username = None 
    email = models.EmailField(_('Email'), unique=True, null=True, blank=True)
    phone_number = models.CharField(_('Telefon'), max_length=15, unique=True, null=True, blank=True)
    address = models.TextField(_('Manzil'), null=True, blank=True)
    avatar = models.ImageField(_('Profil rasmi'), upload_to='avatars/', null=True, blank=True)
    is_verified = models.BooleanField(_('Tasdiqlanganmi'), default=False)
    
    class RoleChoice(models.TextChoices):
        CUSTOMER = 'customer', _('Mijoz')
        SELLER = 'seller', _('Sotuvchi')
        ADMIN = 'admin', _('Admin')
        
    role = models.CharField(_('Rol'), max_length=10, choices=RoleChoice.choices, default=RoleChoice.CUSTOMER)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'  
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email if self.email else self.phone_number

class CodeVerify(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='verification_codes')
    code = models.CharField(_('Kod'), max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(_('Ishlatildi'), default=False)

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=2)