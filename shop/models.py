from django.db import models
from parler.models import TranslatableModel, TranslatedFields
from django.contrib.auth import get_user_model
User = get_user_model()

class Supershop(TranslatableModel):
    translations = TranslatedFields(
        super_shop_name=models.CharField(max_length=255),
        description=models.TextField()
    )
    image = models.ImageField(upload_to='product_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.safe_translation_getter('super_shop_name', any_language=True) or "Unnamed Shop"


class Category(TranslatableModel):
    translations = TranslatedFields(
        category_name=models.CharField(max_length=255),
        description=models.TextField()
    )
    image = models.ImageField(upload_to='category_images/', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.safe_translation_getter('category_name', any_language=True) or "Unnamed Category"


class Product(TranslatableModel):
    translations = TranslatedFields(
        product_name=models.CharField(max_length=255),
        description=models.TextField(),
    )
    uom=models.CharField(max_length=50, blank=True, null=True)  
    product_image1 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    product_image2 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    product_image3 = models.ImageField(upload_to='product_images/', null=True, blank=True)
    category = models.ForeignKey(Category, related_name='products', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.safe_translation_getter('product_name', any_language=True) or "Unnamed Product"



class ProductPrice(models.Model):
    product = models.ForeignKey(Product, related_name='prices', on_delete=models.CASCADE)
    shop = models.ForeignKey(Supershop, related_name='product_prices', on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.shop} - {self.product}: {self.price}"



class Favorite(models.Model):
    user = models.ForeignKey(User, related_name='favorites', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='favorites', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Favorite: {self.user} - {self.product}"
    
    
class ProductSubscription(models.Model):
    user = models.ForeignKey(User, related_name='product_subscriptions', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='product_subscriptions', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Subscription: {self.user} - {self.product}"


class Notification(models.Model):
    user = models.ForeignKey(User, related_name='notifications', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, related_name='notifications', on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.user}: {self.message[:20]}..."
