from rest_framework import serializers # type: ignore
from service.models import Shopping, SelectedSupermarket
from service.serializers.notification_product import get_supermarkets_cached
from service.utils.product_matching import product_matching_service
from service.views.products_views import get_all_products_cached # type: ignore
from django.core.cache import cache # type: ignore

class ShoppingSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(read_only=True)
    product_ids = serializers.ListField(
        child=serializers.IntegerField(min_value=1),
        write_only=True,
        required=True
    )

    class Meta:
        model = Shopping
        fields = ['id', 'user', 'product_id', 'product_ids']
        read_only_fields = ['id','user']
        
    def validate_product_id(self, value):
        user = self.context['request'].user
        exising_product_id = Shopping.objects.filter(user=user, product_id=value).exists()
        
        if exising_product_id:
            raise serializers.ValidationError("This product is already in your shopping list.")
        return value        

    def validate(self, attrs):
        product_ids = attrs.get('product_ids')
        if not product_ids:
            raise serializers.ValidationError({"product_ids": "Provide at least one product id."})
        if len(product_ids) != len(set(product_ids)):
            raise serializers.ValidationError({"product_ids": "Duplicate product ids are not allowed."})
        user = self.context['request'].user
        existing = set(
            Shopping.objects.filter(user=user, product_id__in=product_ids)
            .values_list('product_id', flat=True)
        )
        if existing:
            new_product_ids = [pid for pid in product_ids if pid not in existing]
            if not new_product_ids:
                existing_list = sorted(existing)
                raise serializers.ValidationError({
                    "product_ids": f"All products are already in your shopping list: {existing_list}"
                })
            attrs['product_ids'] = new_product_ids
        return attrs
        
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

            cache_key = 'all_supermarkets_dict'
            supermarket_dict = cache.get(cache_key) or {}
            if not supermarket_dict:
                get_supermarkets_cached()
                supermarket_dict = cache.get(cache_key)
                
            if supermarket_dict:
                product_matches = [
                    match for match in product_matches
                    if match.get('supermarket_id') in supermarket_dict
                ]

            selected_supermarket_ids = list(
                SelectedSupermarket.objects.filter(user=instance.user)
                .values_list('supermarket_id', flat=True)
            )
            selected_supermarket_ids_set = set(selected_supermarket_ids)
            if selected_supermarket_ids_set:
                product_matches = [
                    match for match in product_matches
                    if match.get('supermarket_id') in selected_supermarket_ids_set
                ]
            else:
                product_matches = []
            
            if selected_supermarket_ids_set:
                matches_by_supermarket = {
                    match.get('supermarket_id'): match
                    for match in product_matches
                }
                normalized_matches = []
                for supermarket_id in sorted(selected_supermarket_ids_set):
                    match = matches_by_supermarket.get(supermarket_id)
                    if match:
                        normalized_matches.append({
                            'id': match.get('id'),
                            'name': match.get('name'),
                            'supermarket_id': match.get('supermarket_id'),
                            'supermarket_name': supermarket_dict.get(
                                match.get('supermarket_id'), {}
                            ).get('name'),
                            'price': match.get('price'),
                            'image_url': match.get('image_url'),
                        })
                    else:
                        normalized_matches.append({
                            'id': None,
                            'name': 'None',
                            'supermarket_id': supermarket_id,
                            'supermarket_name': supermarket_dict.get(
                                supermarket_id, {}
                            ).get('name'),
                            'price': None,
                            'image_url': 'None',
                        })
                if product and not any(
                    item.get('id') == instance.product_id for item in normalized_matches
                ):
                    normalized_matches.append({
                        'id': instance.product_id,
                        'name': product.get('name'),
                        'supermarket_id': product.get('supermarket_id'),
                        'supermarket_name': supermarket_dict.get(
                            product.get('supermarket_id'), {}
                        ).get('name'),
                        'price': product.get('price'),
                        'image_url': product.get('image_url'),
                    })
                def _price_key(item):
                    price = item.get('price')
                    try:
                        price_value = float(price)
                    except (TypeError, ValueError):
                        price_value = None
                    return (price_value is None, price_value)

                normalized_matches.sort(key=_price_key)
                representation['matched_products'] = normalized_matches[:3]
            else:
                representation['matched_products'] = None
        else:
            representation["product_name"] = "Unknown Product"
            representation['matched_product_ids'] = []
            representation['matched_products'] = []
        
        return representation



class ListShoppingSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Shopping
        fields = ['id', 'user', 'product_id']
        read_only_fields = ['id','user']
