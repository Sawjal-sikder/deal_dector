from rest_framework import serializers # type: ignore
from service.views.products_views import get_all_products_cached # type: ignore
from ..models import FavoriteProduct # type: ignore

class FavoriteProductSerializer(serializers.ModelSerializer):
    product = serializers.SerializerMethodField()
    class Meta:
        model = FavoriteProduct
        fields = ['id', 'user', 'product_id', 'product', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
        
        
    def validate(self, attrs):
        user = self.context['request'].user
        product_id = attrs.get('product_id')
        
        if FavoriteProduct.objects.filter(user=user, product_id=product_id).exists():
            raise serializers.ValidationError({
                'product_id': 'You have already added this product to favorites.'
            })
        return attrs
    
    def get_product(self, instance):
        all_products = get_all_products_cached()
        return next((p for p in all_products if p.get('id') == instance.product_id), None)
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.full_name or instance.user.email 
        return representation