from rest_framework import generics, permissions, response # type: ignore
from ..models import FavoriteProduct # type: ignore
from ..serializers.favorite_product import FavoriteProductSerializer # type: ignore

class FavoriteProductListCreateView(generics.ListCreateAPIView):
    queryset = FavoriteProduct.objects.all()
    serializer_class = FavoriteProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
class FavoriteProductDetailView(generics.RetrieveDestroyAPIView):
    queryset = FavoriteProduct.objects.all()
    serializer_class = FavoriteProductSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return response.Response({'success': 'Favorite product removed successfully.'}, status=200)