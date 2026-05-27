from django.core.validators import MinValueValidator
from django.db import models
from common.models import BaseModel
 
 
class Status(models.TextChoices):
    PENDING = "pending", "Kutilmoqda"
    PAID = "paid", "To'landi"
    DELIVERING = "delivering", "Yetkazilmoqda"
    COMPLETED = "completed", "Yakunlandi"
    CANCELLED = "cancelled", "Bekor qilindi"
 
 
class Order(BaseModel):
    user = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="orders",
        verbose_name="Foydalanuvchi",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Holati",
    )
    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Umumiy narx",
    )
    shipping_address = models.TextField(null=True, blank=True, verbose_name="Yetkazish manzili")
    note = models.TextField(null=True, blank=True, verbose_name="Izoh")
 
    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ["-created_at"]
 
    def __str__(self):
        return f"Buyurtma #{self.pk} — {self.user}"
 
    @property
    def can_cancel(self):
        return self.status == Status.PENDING
 
 
class OrderItem(BaseModel):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Buyurtma",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.SET_NULL,
        null=True,
        related_name="order_items",
        verbose_name="Mahsulot",
    )
    quantity = models.PositiveIntegerField(verbose_name="Miqdori")
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Narxi (buyurtma paytidagi)",
    )
 
    class Meta:
        verbose_name = "Buyurtma mahsuloti"
        verbose_name_plural = "Buyurtma mahsulotlari"
 
    def __str__(self):
        return f"{self.product} x{self.quantity}"
 
    @property
    def total_price(self):
        return self.price * self.quantity
 
 