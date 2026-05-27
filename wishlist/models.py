from django.db import models
from common.models import BaseModel
 
 
class Wishlist(BaseModel):
    user = models.OneToOneField(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="wishlist",
        verbose_name="Foydalanuvchi",
    )
 
    class Meta:
        verbose_name = "Sevimlilar"
        verbose_name_plural = "Sevimlilar"
 
    def __str__(self):
        return f"{self.user} — sevimlilar"
 
 
class WishlistItem(BaseModel):
    wishlist = models.ForeignKey(
        Wishlist,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Sevimlilar",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="wishlist_items",
        verbose_name="Mahsulot",
    )
 
    class Meta:
        verbose_name = "Sevimli mahsulot"
        verbose_name_plural = "Sevimli mahsulotlar"
        constraints = [
            models.UniqueConstraint(
                fields=["wishlist", "product"],
                name="unique_wishlist_product",
            )
        ]
 
    def __str__(self):
        return f"{self.wishlist.user} — {self.product.title}"
 