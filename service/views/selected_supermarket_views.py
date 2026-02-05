from rest_framework import generics, status, permissions # type: ignore
from rest_framework.response import Response # type: ignore
from service.models import SelectedSupermarket
from service.serializers.selected_supermarket_serializers import SelectedSupermarketSerializer

class SelectedSupermarketListCreateView(generics.ListCreateAPIView):
    queryset = SelectedSupermarket.objects.all()
    serializer_class = SelectedSupermarketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        
class SelectedSupermarketDetailView(generics.RetrieveDestroyAPIView):
    queryset = SelectedSupermarket.objects.all()
    serializer_class = SelectedSupermarketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            "message": "Selected supermarket deleted successfully."
        }, status=status.HTTP_204_NO_CONTENT)