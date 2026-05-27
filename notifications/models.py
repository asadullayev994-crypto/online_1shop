from django.db import models
from django.utils import timezone
from common.models import BaseModel
 
 
class NotificationType(models.TextChoices):
    SYSTEM = "system", "Tizim"
    ORDER = "order", "Buyurtma"
    PAYMENT = "payment", "To'lov"
    PROMOTION = "promotion", "Aksiya"
 
 
class Notification(BaseModel):
    user = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Foydalanuvchi",
    )
    title = models.CharField(max_length=255, verbose_name="Sarlavha")
    message = models.TextField(verbose_name="Xabar")
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
        verbose_name="Turi",
    )
    is_read = models.BooleanField(default=False, verbose_name="O'qildi")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="O'qilgan vaqti")
 
    class Meta:
        verbose_name = "Bildirishnoma"
        verbose_name_plural = "Bildirishnomalar"
        ordering = ["-created_at"]
 
    def __str__(self):
        return self.title
 
    def mark_as_read(self):
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=["is_read", "read_at"])
 
 
class NotificationPreference(BaseModel):
    user = models.OneToOneField(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="notification_preference",
        verbose_name="Foydalanuvchi",
    )
    order_updates = models.BooleanField(default=True, verbose_name="Buyurtma yangilanishlari")
    payment_updates = models.BooleanField(default=True, verbose_name="To'lov yangilanishlari")
    promotions = models.BooleanField(default=True, verbose_name="Aksiyalar")
    system_updates = models.BooleanField(default=True, verbose_name="Tizim xabarlari")
 
    class Meta:
        verbose_name = "Bildirishnoma sozlamalari"
        verbose_name_plural = "Bildirishnoma sozlamalari"
 
    def __str__(self):
        return f"{self.user} — bildirishnoma sozlamalari"
 