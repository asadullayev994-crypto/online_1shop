from django.db import models
from common.models import BaseModel
 
 
class Cart(BaseModel):
    user = models.OneToOneField(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="Foydalanuvchi",
    )
 
    class Meta:
        verbose_name = "Savat"
        verbose_name_plural = "Savatlar"
 
    def __str__(self):
        return f"{self.user} — savat"
 
    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())
 
    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())
 
 
class CartItem(BaseModel):
    cart = models.ForeignKey(
        Cart,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name="Savat",
    )
    product = models.ForeignKey(
        "products.Product",
        on_delete=models.CASCADE,
        related_name="cart_items",
        verbose_name="Mahsulot",
    )
    quantity = models.PositiveIntegerField(default=1, verbose_name="Miqdori")
 
    class Meta:
        verbose_name = "Savat mahsuloti"
        verbose_name_plural = "Savat mahsulotlari"
        unique_together = ["cart", "product"]
 
    def __str__(self):
        return f"{self.product.title} x{self.quantity}"
 
    @property
    def total_price(self):
        return self.product.current_price * self.quantity
 