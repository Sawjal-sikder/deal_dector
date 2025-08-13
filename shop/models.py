from django.db import models
from parler.models import TranslatableModel, TranslatedFields

class Supershop(TranslatableModel):
    translations = TranslatedFields(
        super_shop_name=models.CharField(max_length=255),
        description=models.TextField()
    )

    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # Make sure to return a string, even if no name exists
        return self.safe_translation_getter('super_shop_name', any_language=True) or "Unnamed Shop"
