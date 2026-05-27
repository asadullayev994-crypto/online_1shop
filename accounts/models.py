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
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)
        return self.create_user(email=email, password=password, **extra_fields)


class CustomUser(AbstractUser):
    username = None

    class RoleChoice(models.TextChoices):
        CUSTOMER = "customer", _("Mijoz")
        SELLER = "seller", _("Sotuvchi")
        ADMIN = "admin", _("Admin")

    email = models.EmailField(_("Email"), unique=True, null=True, blank=True)
    phone_number = models.CharField(_("Telefon"), max_length=15, unique=True, null=True, blank=True)
    address = models.TextField(_("Manzil"), null=True, blank=True)
    avatar = models.ImageField(_("Profil rasmi"), upload_to="avatars/", null=True, blank=True)
    is_verified = models.BooleanField(_("Tasdiqlanganmi"), default=False)
    role = models.CharField(
        _("Rol"),
        max_length=10,
        choices=RoleChoice.choices,
        default=RoleChoice.CUSTOMER,
    )

    # Qo'shimcha maydonlar
    last_seen = models.DateTimeField(_("Oxirgi faollik"), null=True, blank=True)
    is_banned = models.BooleanField(_("Bloklangan"), default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _("Foydalanuvchi")
        verbose_name_plural = _("Foydalanuvchilar")

    def __str__(self):
        return self.email if self.email else self.phone_number

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.email


class CodeVerify(models.Model):
    class PurposeChoice(models.TextChoices):
        REGISTER = "register", _("Ro'yxatdan o'tish")
        RESET = "reset", _("Parolni tiklash")

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="verification_codes",
    )
    code = models.CharField(_("Kod"), max_length=6)
    purpose = models.CharField(
        _("Maqsad"),
        max_length=10,
        choices=PurposeChoice.choices,
        default=PurposeChoice.REGISTER,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(_("Ishlatildi"), default=False)

    class Meta:
        verbose_name = _("Tasdiqlash kodi")
        verbose_name_plural = _("Tasdiqlash kodlari")
        ordering = ["-created_at"]

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(random.randint(100000, 999999))
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.created_at + timedelta(minutes=2)

    def __str__(self):
        return f"{self.user} - {self.code} ({self.purpose})"


class ActivityLog(models.Model):
    """Foydalanuvchi faollik tarixi"""

    class ActionChoice(models.TextChoices):
        LOGIN = "login", _("Kirish")
        LOGOUT = "logout", _("Chiqish")
        PASSWORD_CHANGE = "password_change", _("Parol o'zgartirish")
        PROFILE_UPDATE = "profile_update", _("Profil yangilash")
        REGISTER = "register", _("Ro'yxatdan o'tish")

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="activity_logs",
    )
    action = models.CharField(_("Harakat"), max_length=20, choices=ActionChoice.choices)
    ip_address = models.GenericIPAddressField(_("IP manzil"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Faollik tarixi")
        verbose_name_plural = _("Faollik tarixlari")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user} - {self.action} - {self.created_at}"