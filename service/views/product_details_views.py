from rest_framework.views import APIView  # type: ignore
from rest_framework.response import Response  # type: ignore
from rest_framework import permissions, status #type: ignore
from service.views.products_views import get_all_products_cached  # type: ignore
from service.utils.product_matching import product_matching_service
from service.serializers.notification_product import get_supermarkets_cached



class ProductDetailsView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, product_id):
        try:
            product_id = int(product_id)
        except (ValueError, TypeError):
            return Response({'error': 'Invalid product id'}, status=400)

        all_products = get_all_products_cached()

        if all_products is None:
            return Response(
                {'error': 'Service temporarily unavailable. Please try again later.'},
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        product = next(
            (p for p in all_products if p.get('id') == product_id),
            None
        )

        if not product:
            return Response({'error': 'Product not found'}, status=404)

        # product matching from related supermarkets
        product_matching_ids = product_matching_service(
            product_id=product.get('id'),
            supermarket_id=product.get('supermarket_id')
        )

        # matched products lookup (set for O(1) membership check)
        all_matching_ids = {product_id, *(product_matching_ids or [])}
        supermarkets = get_supermarkets_cached()
        matching_products = sorted(
            [
                {
                    "id": p.get("id"),
                    "name": p.get("name"),
                    "supermarket_id": p.get("supermarket_id"),
                    "supermarket_name": supermarkets.get(p.get("supermarket_id"), {}).get("name"),
                    "supermarket_logo": supermarkets.get(p.get("supermarket_id"), {}).get("logo_url"),
                    "price": p.get("price"),
                }
                for p in all_products if p.get("id") in all_matching_ids
            ],
            key=lambda p: float(p.get("price") or 0)
        )

        return Response({
            "id": product.get("id"),
            "name": product.get("name"),
            "brand": product.get("brand"),
            "description": product.get("description"),
            "category_id": product.get("category_id"),
            "supermarket_id": product.get("supermarket_id"),
            "price": product.get("price"),
            "price_per_unit": product.get("price_per_unit"),
            "unit_amount": product.get("unit_amount"),
            "image_url": product.get("image_url"),
            "updated_at": product.get("updated_at"),
            "matching_products": matching_products
        })
