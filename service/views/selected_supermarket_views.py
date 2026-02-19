from rest_framework import generics, status, permissions # type: ignore
from rest_framework.response import Response # type: ignore
from service.models import SelectedSupermarket
from service.serializers.selected_supermarket_serializers import (
    SelectedSupermarketSerializer,
    SelectedSupermarketBulkCreateSerializer,
)

class SelectedSupermarketListCreateView(generics.ListCreateAPIView):
    queryset = SelectedSupermarket.objects.all()
    serializer_class = SelectedSupermarketSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = SelectedSupermarketBulkCreateSerializer(
            data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        created = serializer.save()
        return Response(
            SelectedSupermarketSerializer(created, many=True).data,
            status=status.HTTP_201_CREATED,
        )
        
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