# signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import ProductPrice, Notification, ProductSubscription

@receiver(pre_save, sender=ProductPrice)
def notify_price_change(sender, instance, **kwargs):
    if not instance.pk:
        return  # New price record, no old value to compare

    try:
        old_price = ProductPrice.objects.get(pk=instance.pk)
        if old_price.price != instance.price:
            change_type = "increased" if instance.price > old_price.price else "decreased"

            product_name = instance.product.safe_translation_getter('product_name', any_language=True)
            shop_name = instance.shop.safe_translation_getter('super_shop_name', any_language=True)

            message = f"The price of {product_name} at {shop_name} has {change_type} from {old_price.price} to {instance.price}"

            # Get all users subscribed to the product
            subscribers = ProductSubscription.objects.filter(product=instance.product)
            for sub in subscribers:
                Notification.objects.create(
                    user=sub.user,
                    product=instance.product,
                    message=message
                )
    except ProductPrice.DoesNotExist:
        # Handle case where old price doesn't exist
        pass
