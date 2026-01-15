from rest_framework import generics, permissions, response # type: ignore
from ..models import NotificationProducts # type: ignore
from ..serializers.notification_product import NotificationProductsSerializer # type: ignore

class NotificationProductsListCreateView(generics.ListCreateAPIView):
    queryset = NotificationProducts.objects.all()
    serializer_class = NotificationProductsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
    
    
class NotificationProductsDeleteView(generics.DestroyAPIView):
    queryset = NotificationProducts.objects.all()
    serializer_class = NotificationProductsSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return response.Response({"message": "Notification product deleted successfully."}, status=204)