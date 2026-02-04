from rest_framework import serializers # type: ignore
from service.models import Shopping
from service.utils.product_matching import product_matching_service
from service.views.products_views import get_all_products_cached # type: ignore

class ShoppingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shopping
        fields = ['id', 'user', 'product_id']
        read_only_fields = ['id','user']
        
    def validate_product_id(self, value):
        user = self.context['request'].user
        exising_product_id = Shopping.objects.filter(user=user, product_id=value).exists()
        
        if exising_product_id:
            raise serializers.ValidationError("This product is already in your shopping list.")
        return value        
        
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = instance.user.full_name or instance.user.email
        products = get_all_products_cached()
        product = next((p for p in products if p.get('id') == instance.product_id), None)
        if product:
            representation["product_name"] = product.get("name", "sample product name")
            
            product_match_ids = product_matching_service(
                product_id=instance.product_id,
                supermarket_id=product.get('supermarket_id')
            )
            # representation['matched_product_ids'] = product_match_ids
            # Get full product details for matched IDs
            product_matches = [
                p for p in products if p.get('id') in product_match_ids
                
            ]
            
            product_matches = [
                {
                    'id': match.get('id'),
                    'name': match.get('name'),
                    'supermarket_id': match.get('supermarket_id'),
                    'price': match.get('price'),
                    'image_url': match.get('image_url'),
                }
                for match in product_matches
            ]
            
            representation['matched_products'] = product_matches
        else:
            representation["product_name"] = "Unknown Product"
            representation['matched_product_ids'] = []
            representation['matched_products'] = []
        
        return representation
