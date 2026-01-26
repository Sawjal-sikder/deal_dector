from rest_framework import generics, permissions, response # type: ignore
from service.utils.product_matching import product_matching_service
from service.views.products_views import get_all_products_cached # type: ignore
from service.models import FavoriteProduct # type: ignore
from service.serializers.favorite_product import FavoriteProductSerializer # type: ignore
from rest_framework import status # type: ignore
from django.core.cache import cache # type: ignore
from service.utils.fetch_mysql_data import DB_Query

class FavoriteProductListCreateView(generics.ListCreateAPIView):
    queryset = FavoriteProduct.objects.all()
    serializer_class = FavoriteProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

        


class FavoriteProductDetailView(generics.RetrieveDestroyAPIView):
    queryset = FavoriteProduct.objects.all()  # Removed select_related('product')
    serializer_class = FavoriteProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        data = serializer.data
        
        # product_id is stored directly on FavoriteProduct (not a FK relation)
        product_id = instance.product_id
        supermarket_id = data.get('product', {}).get('supermarket_id', 1)

        # Get matching products
        matching_product_ids = product_matching_service(product_id, supermarket_id)
        
        if not matching_product_ids:
            data['matching_products'] = []
            return response.Response(data, status=status.HTTP_200_OK)

        # Get cached products and filter in one pass
        all_products = get_all_products_cached()
        
        # Create lookup set for O(1) access
        matching_ids_set = set(matching_product_ids)
        matching_products = [
            prod for prod in all_products 
            if prod['id'] in matching_ids_set
        ] if all_products else []

        if not matching_products:
            data['matching_products'] = []
            return response.Response(data, status=status.HTTP_200_OK)

        # Get supermarkets with caching
        supermarket_dict = self._get_supermarkets_cached()
        
        # Build response in single list comprehension
        data['matching_products'] = [
            {
                "name": prod.get('name'),
                "supermarket_name": supermarket_dict.get(prod.get('supermarket_id'), {}).get('name'),
                "price": prod.get('price'),
                "original_price": prod.get('price_per_unit'),
            }
            for prod in matching_products
        ]
        
        return response.Response(data, status=status.HTTP_200_OK)

    @staticmethod
    def _get_supermarkets_cached():
        """Cache supermarkets to avoid repeated DB queries"""
        cache_key = 'all_supermarkets_dict'
        supermarket_dict = cache.get(cache_key)
        
        if supermarket_dict is None:
            query = "SELECT * FROM supermarkets;"
            supermarkets = list(DB_Query(query=query))
            supermarket_dict = {shop['id']: shop for shop in supermarkets}
            cache.set(cache_key, supermarket_dict, timeout=3600)
        
        return supermarket_dict

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return response.Response(
            {'success': 'Favorite product removed successfully.'}, 
            status=status.HTTP_200_OK
        )