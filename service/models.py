from django.db import models #type: ignore
from django.contrib.auth import get_user_model # type: ignore
User = get_user_model()

class FavoriteProduct(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

        
    def __str__(self):
        return f"User {self.user_id} - Product {self.product_id}"
    
    
class NotificationProducts(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

        
    def __str__(self):
        return f"User {self.user_id} - Product {self.product_id}"