from rest_framework import generics, permissions, response # type: ignore
from service.models import Shopping # type: ignore
from service.serializers.shopping_serializer import ShoppingSerializer, ListShoppingSerializer # type: ignore
from rest_framework import status # type: ignore

class ShoppingListCreateView(generics.ListCreateAPIView):
    queryset = Shopping.objects.all()
    serializer_class = ShoppingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def _group_by_supermarket(self, shopping_items):
        supermarkets = {}
        for item in shopping_items:
            for match in item.get('matched_products') or []:
                if match.get('id') is None:
                    continue
                supermarket_id = match.get('supermarket_id')
                if supermarket_id is None:
                    continue
                supermarket = supermarkets.setdefault(supermarket_id, {
                    "supermarket_id": supermarket_id,
                    "supermarket_name": match.get('supermarket_name'),
                    "products": [],
                })
                supermarket["products"].append({
                    "id": match.get('id'),
                    "name": match.get('name'),
                    "price": match.get('price'),
                    "image_url": match.get('image_url'),
                })
        grouped = [supermarkets[key] for key in sorted(supermarkets)]
        for group in grouped:
            group["products"] = sorted(
                group["products"],
                key=lambda prod: prod.get('price') if prod.get('price') is not None else float('inf'),
            )
        return grouped

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user, is_shopping=True)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        if isinstance(request.data, dict) and request.data.get('product_ids') is not None:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            product_ids = serializer.validated_data['product_ids']
            items = [Shopping(user=request.user, product_id=pid) for pid in product_ids]
            Shopping.objects.bulk_create(items)
            created = Shopping.objects.filter(
                user=request.user,
                product_id__in=product_ids
            ).order_by('-id')
            output = ShoppingSerializer(
                created,
                many=True,
                context=self.get_serializer_context()
            )
            grouped = self._group_by_supermarket(output.data)
            return response.Response(grouped, status=status.HTTP_201_CREATED)

        return super().create(request, *args, **kwargs)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        output = self.get_serializer(
            queryset,
            many=True,
            context=self.get_serializer_context()
        )
        grouped = self._group_by_supermarket(output.data)
        return response.Response(grouped, status=status.HTTP_200_OK)
        
        
class ShoppingDetailView(generics.RetrieveDestroyAPIView):
    queryset = Shopping.objects.all()
    serializer_class = ShoppingSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'product_id'

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return response.Response({
            "message": "Shopping item deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)




class ListShoppingView(generics.ListAPIView):
    queryset = Shopping.objects.all()
    serializer_class = ListShoppingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
