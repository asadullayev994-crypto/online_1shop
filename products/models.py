from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from common.models import BaseModel
from common.mixins import AutoSlugMixin
 
 
class Status(models.TextChoices):
    DRAFT = "draft", "Qoralama"
    PUBLISHED = "published", "E'lon berilgan"
    OUT_OF_STOCK = "out_of_stock", "Tugagan"
    ARCHIVED = "archived", "Arxivlangan"
 
 
class Product(AutoSlugMixin, BaseModel):
    slug_source_field = "title"
 
    seller = models.ForeignKey(
        "accounts.CustomUser",
        on_delete=models.CASCADE,
        related_name="products",
        null=True,
        blank=True,
        verbose_name="Sotuvchi",
    )
    category = models.ForeignKey(
        "categories.Category",
        on_delete=models.SET_NULL,
        null=True,
        related_name="products",
        verbose_name="Kategoriya",
    )
    title = models.CharField(max_length=255, verbose_name="Nomi")
    slug = models.SlugField(unique=True)
    description = models.TextField(verbose_name="Tavsif")
    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        verbose_name="Narxi",
    )
    discount_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        verbose_name="Chegirmali narx",
    )
    stock = models.PositiveIntegerField(default=0, verbose_name="Ombordagi miqdor")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        verbose_name="Holati",
    )
 
    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ["-created_at"]
 
    def __str__(self):
        return self.title
 
    def clean(self):
        if self.discount_price and self.discount_price >= self.price:
            raise ValidationError({"discount_price": "Chegirmali narx asosiy narxdan kichik bo'lishi kerak."})
 
    @property
    def current_price(self):
        return self.discount_price if self.discount_price else self.price
 
    @property
    def discount_percent(self):
        if self.discount_price and self.price > 0:
            return round((1 - self.discount_price / self.price) * 100)
        return 0
 
    @property
    def is_available(self):
        return self.stock > 0 and self.status == Status.PUBLISHED
 
    @property
    def main_image(self):
        return self.images.filter(is_main=True).first()
 
 
class ProductImage(BaseModel):
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="images",
        verbose_name="Mahsulot",
    )
    image = models.ImageField(upload_to="products/", verbose_name="Rasm")
    is_main = models.BooleanField(default=False, verbose_name="Asosiy rasmmi")
 
    class Meta:
        verbose_name = "Mahsulot rasmi"
        verbose_name_plural = "Mahsulot rasmlari"
 
    def __str__(self):
        return f"{self.product.title} — rasm"
 
    def save(self, *args, **kwargs):
        if self.is_main:
            ProductImage.objects.filter(product=self.product, is_main=True).update(is_main=False)
        super().save(*args, **kwargs)