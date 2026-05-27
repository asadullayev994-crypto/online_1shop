from django.db import models
from common.models import BaseModel
from common.mixins import AutoSlugMixin
 
 
class Category(AutoSlugMixin, BaseModel):
    name = models.CharField(max_length=255, verbose_name="Nomi")
    slug = models.SlugField(unique=True)
    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Ota kategoriya",
    )
    image = models.ImageField(upload_to="categories/", null=True, blank=True)
 
    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ["name"]
 
    def __str__(self):
        return self.name
 
    @property
    def full_path(self):
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name
 
 