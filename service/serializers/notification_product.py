from rest_framework import serializers # type: ignore
from ..models import NotificationProducts # type: ignore
from service.views.products_views import get_all_products_cached # type: ignore

class NotificationProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationProducts
        fields = ['id', 'user', 'product_id']
        read_only_fields = ['id','user']
        
        
    def validate(self, attrs):
        user = self.context['request'].user
        product_id = attrs.get('product_id')
        
        if NotificationProducts.objects.filter(user=user, product_id=product_id).exists():
            raise serializers.ValidationError({
                'product_id': 'You have already added this product to notifications.'
            })
        return attrs

        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.full_name or instance.user.email 
        representation['product_name'] = None
        all_products = get_all_products_cached()
        product = next((p for p in all_products if p.get('id') == instance.product_id), None)
        if product:
            representation['product_name'] = product.get('name')
        return representation    