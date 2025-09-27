from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from payment.paymentPermission import HasActiveSubscription
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
    
    # permission_classes = [HasActiveSubscription]
    
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
class CategoryByProductsView(generics.ListAPIView):
    serializer_class = CategoryProductsSerializer
    
    def get_queryset(self):
        category_id = self.kwargs.get("category_id")
        if category_id:
            return Category.objects.filter(id=category_id).prefetch_related('products__prices__shop')
        return Category.objects.all().prefetch_related('products__prices__shop')
    


class CategoryByProductsByShopView(generics.ListAPIView):
    serializer_class = CategoryProductsByShopSerializer

    def get_queryset(self):
        shop_ids = self.kwargs.get("shop_ids")
        qs = Category.objects.all().prefetch_related("products__prices__shop")

        if shop_ids:
            shop_ids_list = [int(i) for i in shop_ids.split(",")]
            # filter only categories/products that have those shop prices
            qs = qs.filter(products__prices__shop_id__in=shop_ids_list).distinct()
            self.shop_ids_list = shop_ids_list
        else:
            self.shop_ids_list = None

        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["shop_ids"] = getattr(self, "shop_ids_list", None)
        return context
    


# create and Delete favorite products
class FavoriteCreateDeleteView(APIView):  

    def post(self, request, product_id=None):
        product = get_object_or_404(Product, id=product_id)
        
        # Check if the product is already in favorites
        existing_favorite = Favorite.objects.filter(user=request.user, product=product).first()
        if existing_favorite:
            serializer = FavoriteCreateDeleteSerializer(existing_favorite)
            return Response(
                {"message": "This product is already in favorites.", "Favorite Item": serializer.data},
                status=status.HTTP_200_OK
            )
        
        # Get user's favorite item limit and current count
        user = request.user
        favorite_balance = user.favorite_item
        favorite_item_used = Favorite.objects.filter(user=user).count()
        
        # Check if user has reached the limit
        if favorite_item_used >= favorite_balance:
            return Response(
                {"message": "You have reached your favorite item limit."},
                status=status.HTTP_403_FORBIDDEN
            )

        # Create the favorite item
        favorite = Favorite.objects.create(user=request.user, product=product)
        serializer = FavoriteCreateDeleteSerializer(favorite)
        return Response(
            {"message": "Favorite created successfully.", "Favorite Item": serializer.data},
            status=status.HTTP_201_CREATED
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
    
    
# create and Delete favorite products
class WishlistCreateDeleteView(APIView):  

    def post(self, request, product_id=None):
        product = get_object_or_404(Product, id=product_id)
        wishlist, created = Wishlist.objects.get_or_create(user=request.user, product=product)

        if created:
            serializer = WishlistCreateDeleteSerializer(wishlist)
            return Response(
                {"message": "Wishlist created successfully.", "Wishlist Item": serializer.data},
                status=status.HTTP_201_CREATED
            )
        else:
            serializer = WishlistCreateDeleteSerializer(wishlist)
            return Response(
                {"message": "This product is already in your wishlist.", "Wishlist Item": serializer.data},
                status=status.HTTP_200_OK
            )

    def delete(self, request, product_id=None):
        wishlist = Wishlist.objects.filter(user=request.user, product_id=product_id).first()
        if not wishlist:
            return Response(
                {"message": "This product is not in your wishlist."},
                status=status.HTTP_404_NOT_FOUND
            )
        wishlist.delete()
        return Response({"message": "Wishlist deleted successfully."}, status=status.HTTP_200_OK)

    
class WishlistView(generics.ListAPIView):
    serializer_class = WishlistListSerializer

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product', 'user')


    
    
# create and Delete ShoppingList
class ShoppingListCreateDeleteView(APIView):

    def post(self, request):
        # Try to get product_ids from request body first, then from query parameters
        product_ids = request.data.get("product_ids", [])
        
        # If not found in body, check query parameters
        if not product_ids:
            query_product_ids = request.GET.get("product_ids")
            if query_product_ids:
                try:
                    # Split comma-separated string and convert to integers
                    product_ids = [int(pid.strip()) for pid in query_product_ids.split(",") if pid.strip()]
                except ValueError:
                    return Response(
                        {"error": "Invalid product_ids format in query parameters. Use comma-separated integers."},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        
        if not isinstance(product_ids, list) or not product_ids:
            return Response(
                {"error": "You must provide a list of product_ids either in request body or as query parameter."},
                status=status.HTTP_400_BAD_REQUEST
            )

        created_items = []
        already_existing = []

        for pid in product_ids:
            product = get_object_or_404(Product, id=pid)
            shopping_list, created = ShoppingList.objects.get_or_create(user=request.user, product=product)

            serializer = ShoppingListCreateDeleteSerializer(shopping_list)

            if created:
                created_items.append(serializer.data)
            else:
                already_existing.append(serializer.data)

        return Response(
            {
                "message": "Processed shopping list items.",
                "created_items": created_items,
                "already_existing": already_existing,
            },
            status=status.HTTP_201_CREATED if created_items else status.HTTP_200_OK
        )

    def delete(self, request, product_id=None):
        shopping_list = ShoppingList.objects.filter(user=request.user, product_id=product_id).first()
        if not shopping_list:
            return Response(
                {"message": "This product is not in your shopping list."},
                status=status.HTTP_404_NOT_FOUND
            )
        shopping_list.delete()
        return Response({"message": "ShoppingList deleted successfully."}, status=status.HTTP_200_OK)


class ShoppingListView(generics.ListAPIView):
    serializer_class = ShoppingListListSerializer

    def get_queryset(self):
        return ShoppingList.objects.filter(user=self.request.user).select_related('product', 'user')


    
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