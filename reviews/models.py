from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from common.models import BaseModel
 
 
class Review(BaseModel):
    user = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Foydalanuvchi",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="reviews",
        verbose_name="Mahsulot",
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Baho (1-5)",
    )
    title = models.CharField(max_length=255, blank=True, verbose_name="Sarlavha")
    comment = models.TextField(blank=True, verbose_name="Izoh")
    is_approved = models.BooleanField(default=False, verbose_name="Tasdiqlangan")
 
    class Meta:
        verbose_name = "Sharh"
        verbose_name_plural = "Sharhlar"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["user", "product"],
                name="unique_user_product_review",
            )
        ]
 
    def __str__(self):
        return f"{self.user} — {self.product.title} ({self.rating}★)"