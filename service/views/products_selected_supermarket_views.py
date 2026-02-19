from rest_framework.response import Response
from rest_framework import permissions, status
from rest_framework.views import APIView

from service.models import SelectedSupermarket
from service.views.products_views import get_all_products_cached


class ProductsSelectedSupermarketViews(APIView):
    permission_classes = [permissions.IsAuthenticated]
    # permission_classes = [permissions.AllowAny]

    def get(self, request):
        selected_supermarket = SelectedSupermarket.objects.filter(
            user=request.user
        )

        if not selected_supermarket:
            return Response(
                {"detail": "No supermarket selected"},
                status=status.HTTP_404_NOT_FOUND
            )

        supermarket_ids = list(selected_supermarket.values_list("supermarket_id", flat=True))
        
        all_products = get_all_products_cached()

        if all_products is None:
            return Response(
                {"detail": "Failed to fetch products"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        filtered_products = [
            p for p in all_products
            if p.get('supermarket_id') in supermarket_ids
        ]
        
        selected_products = [
            {
                "id": p.get('id'),
                "name": p.get('name'),
                # "category_id": p.get('category_id'),
                "supermarket_id": p.get('supermarket_id'),
                "description": p.get('description'),
                "price": p.get('price'),
                "original_price": p.get('original_price'),
            }
            for p in filtered_products
        ]

        return Response(
            selected_products,
            status=status.HTTP_200_OK
        )
