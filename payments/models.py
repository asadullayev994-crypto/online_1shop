from django.core.validators import MinValueValidator
from django.db import models
from common.models import BaseModel
 
 
class PaymentMethod(models.TextChoices):
    CASH = "cash", "Naqd"
    CARD = "card", "Karta"
    TRANSFER = "transfer", "O'tkazma"
 
 
class PaymentStatus(models.TextChoices):
    PENDING = "pending", "Kutilmoqda"
    PROCESSING = "processing", "Jarayonda"
    PAID = "paid", "To'landi"
    FAILED = "failed", "Muvaffaqiyatsiz"
    REFUNDED = "refunded", "Qaytarildi"
 
 
class Payment(BaseModel):
    order = models.ForeignKey(
        "orders.Order",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Buyurtma",
    )
    user = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name="Foydalanuvchi",
    )
    method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        verbose_name="To'lov usuli",
    )
    status = models.CharField(
        max_length=20,
        choices=PaymentStatus.choices,
        default=PaymentStatus.PENDING,
        verbose_name="Holati",
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Summa",
    )
    currency = models.CharField(max_length=10, default="UZS", verbose_name="Valyuta")
    transaction_id = models.CharField(
        max_length=255,
        unique=True,
        null=True,
        blank=True,
        verbose_name="Tranzaksiya ID",
    )
    provider = models.CharField(max_length=100, blank=True, verbose_name="To'lov tizimi")
    paid_at = models.DateTimeField(null=True, blank=True, verbose_name="To'langan vaqti")
 
    class Meta:
        verbose_name = "To'lov"
        verbose_name_plural = "To'lovlar"
        ordering = ["-created_at"]
 
    def __str__(self):
        return f"Buyurtma #{self.order_id} — {self.get_status_display()}"
 