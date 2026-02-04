from rest_framework import generics, permissions, response # type: ignore
from service.models import Shopping # type: ignore
from service.serializers.shopping_serializer import ShoppingSerializer # type: ignore
from rest_framework import status # type: ignore

class ShoppingListCreateView(generics.ListCreateAPIView):
    queryset = Shopping.objects.all()
    serializer_class = ShoppingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
        
class ShoppingDetailView(generics.RetrieveDestroyAPIView):
    queryset = Shopping.objects.all()
    serializer_class = ShoppingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return response.Response({
            "message": "Shopping item deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)