from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework import generics
from .models import *
from .serializers import *

class SupershopListCreateView(generics.ListCreateAPIView):
    queryset = Supershop.objects.all()
    serializer_class = SupershopSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)
   
class CategoryListCreateView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    


class ProductListView(generics.ListCreateAPIView):
    queryset = Product.objects.all().prefetch_related('prices__shop', 'images', 'category')
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    permission_classes = []  # Temporarily disable authentication for testing
    
    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ProductCreateSerializer
        return ProductListSerializer



class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.all().prefetch_related('prices__shop', 'images', 'category')
    serializer_class = ProductCreateSerializer
    
    
    
class ProductPriceCreateView(generics.ListCreateAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductPriceCreateSerializer
