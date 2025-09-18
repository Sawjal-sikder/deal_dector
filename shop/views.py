from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from .pagination import StandardResultsSetPagination
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework import status
from .serializers import *
from .models import *

class SupershopListCreateView(generics.ListCreateAPIView):
    queryset = Supershop.objects.all()
    serializer_class = SupershopSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    permission_classes = [AllowAny]  

class SupershopDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Supershop.objects.all()
    serializer_class = SupershopUpdateSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)
    permission_classes = [AllowAny]  
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


class ProductUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all().prefetch_related('prices__shop', 'category')
    parser_classes = (MultiPartParser, FormParser, JSONParser)
    serializer_class = ProductSerializer
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"Message": "Product deleted successfully."}, status=204)
    
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


class ProductPriceUpdateView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ProductPrice.objects.all()
    serializer_class = ProductPriceCreateSerializer
    permission_classes = [AllowAny]
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        # Allow partial updates with PATCH
        if request.method.lower() == "patch":
            kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({"message": "Price deleted successfully."}, status=204)


# list of category wise products
class CategoryProductsView(generics.ListAPIView):
    queryset = Category.objects.all().prefetch_related('products__prices__shop')
    serializer_class = CategoryProductsSerializer
    http_method_names = ['get']

# create and Delete favorite products
class FavoriteCreateDeleteView(APIView):  

    def post(self, request, product_id=None):
        product = get_object_or_404(Product, id=product_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, product=product)

        if created:
            serializer = FavoriteCreateDeleteSerializer(favorite)
            return Response(
                {"message": "Favorite created successfully.", "Favorite Item": serializer.data},
                status=status.HTTP_201_CREATED
            )
        else:
            serializer = FavoriteCreateDeleteSerializer(favorite)
            return Response(
                {"message": "This product is already in favorites.", "Favorite Item": serializer.data},
                status=status.HTTP_200_OK
            )

    def delete(self, request, product_id=None):
        favorite = Favorite.objects.filter(user=request.user, product_id=product_id).first()
        if not favorite:
            return Response(
                {"message": "This product is not in your favorites."},
                status=status.HTTP_404_NOT_FOUND
            )
        favorite.delete()
        return Response({"message": "Favorite deleted successfully."}, status=status.HTTP_200_OK)
    
    
class FavoriteView(generics.ListAPIView):
    serializer_class = FavoriteListSerializer

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('product', 'user')
    
    
    
class ToggleSubscriptionView(APIView):

    def post(self, request, product_id, *args, **kwargs):
        product = get_object_or_404(Product, id=product_id)

        subscription, created = ProductSubscription.objects.get_or_create(
            user=request.user, product=product
        )
        
        if not created:
            subscription.delete()
            return Response(
                {"message": "Unsubscribed from product notifications."}, 
                status=status.HTTP_200_OK
            )
        
        return Response(
            {"message": "Subscribed to product notifications."}, 
            status=status.HTTP_201_CREATED
        )



class UserNotificationsView(generics.ListAPIView):
    serializer_class = NotificationSerializer

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    
class UseNotificationsView(APIView):

    def get(self, request, pk):
        """Retrieve a single notification"""
        notification = get_object_or_404(Notification, user=request.user, pk=pk)
        serializer = UseNotificationSerializer(notification)
        return Response(serializer.data)

    def post(self, request, pk, *args, **kwargs):
        """Update notification as read/unread"""
        is_read = request.data.get("is_read")

        if is_read is None:
            return Response(
                {"error": "is_read field is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        notification = get_object_or_404(Notification, user=request.user, pk=pk)
        notification.is_read = is_read
        notification.save()

        return Response(
            {"message": f"Notification is_read={is_read}"},
            status=status.HTTP_200_OK
        )