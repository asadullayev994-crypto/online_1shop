from django.utils.text import slugify
 
 
class AutoSlugMixin:
    slug_source_field = "name"
 
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(getattr(self, self.slug_source_field))
            slug = base_slug
            counter = 1
            while self.__class__.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
 