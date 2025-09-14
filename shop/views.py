from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from .pagination import StandardResultsSetPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import generics, filters
from .serializers import *
from .models import *

class SupershopListCreateView(generics.ListCreateAPIView):
    queryset = Supershop.objects.all()
    serializer_class = SupershopSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    permission_classes = [AllowAny]  # Allow testing without auth

class SupershopDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Supershop.objects.all()
    serializer_class = SupershopUpdateSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    permission_classes = [AllowAny]  # Allow testing without auth
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        # Let PATCH be partial, but keep PUT strict
        if request.method.lower() == "patch":
            kwargs['partial'] = True
        return super().update(request, *args, **kwargs)
    
    # after delete, return 204 No Content and return message
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"Message": "Supershop deleted successfully."}, status=204)

class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    
    def perform_create(self, serializer):
        serializer.save()
        
class CategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryUpdateSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    lookup_field = 'pk'
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"Message": "Category deleted successfully."}, status=204)


class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all().prefetch_related('prices__shop', 'category')
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = ProductSerializer
    
class ProductView(generics.ListAPIView):
    queryset = Product.objects.all().prefetch_related('prices__shop', 'category')
    serializer_class = ProductListSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['translations__product_name', 'translations__description', 'category__translations__category_name']
    ordering_fields = ['translations__product_name', 'created_at', 'updated_at']
    ordering = ['-created_at']  
    
class ProductDetailsonlyView(generics.RetrieveAPIView):
    serializer_class = ProductListSerializer
    queryset = Product.objects.all().prefetch_related('prices__shop', 'category')
    http_method_names = ['get']




class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all().prefetch_related('prices__shop', 'category')
    serializer_class = ProductSerializer
    
    
    
class ProductPriceCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductPriceCreateSerializer


# list of category wise products
class CategoryProductsView(generics.ListAPIView):
    queryset = Category.objects.all().prefetch_related('products__prices__shop')
    serializer_class = CategoryProductsSerializer
    http_method_names = ['get']
