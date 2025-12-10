from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from payment.paymentPermission import HasActiveSubscription
from .pagination import StandardResultsSetPagination
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from rest_framework import generics, filters
from rest_framework import status
from .serializers import *
from datetime import date
from .models import *
from django.core.cache import cache


# form mysql fetch
from .fetch_mysql import DB_Query
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions

# from mysql fetch
class AllTablesMySQLView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def get(self, request):
        data = DB_Query()
        data = {
            "total_count": len(data),
            "current_discounts": data
        }
        return Response({"tables": data})
    

class CurrentDiscountsMySQLView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        query = "SELECT * FROM current_discounts;"
        data = DB_Query(query=query)
        return Response({
            "total_products": len(data),
            "current_discounts": data
                        })
        
        
class ProductMySQLView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        query = "SELECT * FROM products;"
        data = DB_Query(query=query)
        return Response({
            "total_products": len(data),
            "products": data
                        })
        

class ProductDetailsMySQLView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request, product_id):
        query = f"SELECT * FROM products WHERE product_id = {product_id};"
        data = DB_Query(query=query)
        if data:
            return Response({"product_details": data[0]})
        else:
            return Response({"message": "Product not found."}, status=404)  


class CategoryMySQLView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        query = "SELECT * FROM categories;"
        data = DB_Query(query=query)
        return Response({
            "total_categories": len(data),
            "categories": data
                        })


class SupermarketMySQLView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        query = "SELECT * FROM supermarkets;"
        data = DB_Query(query=query)
        return Response({
            "total_supermarkets": len(data),
            "supermarkets": data
                        })


class CategoryWiseProductsMySQLView(APIView):
    permission_classes = [permissions.AllowAny]
    def get(self, request):
        category_name = request.query_params.get("category_name")
        
        if category_name == "" or category_name is None or category_name.lower() == "all":
            query = "SELECT * FROM current_discounts;"
            data = DB_Query(query=query)
            return Response({
                "total_products": len(data),
                "products": data
                            })
        else:
            query = f"SELECT * FROM current_discounts WHERE category_name = '{category_name}';"
            data = DB_Query(query=query)
            return Response({
                f"total_{category_name}_products": len(data),
                "products": data
                            })



# create and Delete favorite products
class FavoriteCreateDeleteView(APIView):  
    # permission_classes = [HasActiveSubscription]

    def post(self, request, product_id=None):        
        user = request.user

        # Check if the product is already in favorites
        existing_favorite = Favorite.objects.filter(user=user, product_id=product_id).first()
        if existing_favorite:
            # if it exists, delete it (toggle behavior)
            existing_favorite.delete()
            return Response(
                {"message": "This product deleted from favorites."},
                status=status.HTTP_204_NO_CONTENT
            )

        # Check current_discounts table
        cache_key = f"current_discount_{product_id}"
        data = cache.get(cache_key)

        if not data:
            # Safe: ensure product_id is int to avoid SQL injection
            try:
                product_id = str(product_id)
            except ValueError:
                return Response(
                    {"message": "Invalid product ID."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Query
            query = f"SELECT id, product_id, name, price FROM current_discounts WHERE product_id = {product_id} LIMIT 1;"
            data = DB_Query(query=query)
            
            if data:
                cache.set(cache_key, data[0], timeout=300)  # cache for 5 minutes

        if not data:
            return Response(
                {"message": "This product does not exist in current discounts."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Create the favorite
        favorite = Favorite.objects.create(user=user, product_id=product_id)
        serializer = FavoriteSerializer(favorite)
        return Response(
            {"message": "Favorite created successfully.", "favorite": serializer.data},
            status=status.HTTP_201_CREATED
        )
        
        
        
class FavoriteView(generics.ListAPIView):
    serializer_class = FavoriteSerializer
    # permission_classes = [HasActiveSubscription]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user)
    
    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        
        # Fetch product details from MySQL for each favorite
        product_data = []
        for product in queryset:
            product_id = product.product_id
            print("Fetching product_id:", product_id)
            # query = f"SELECT * FROM products WHERE product_id = 750706;"
            query = f"SELECT * FROM products WHERE product_id = {product_id};"
            data = DB_Query(query=query)
            if data:
                product_info = data[0]
                product_info['favorite_id'] = product.id
                product_info['created_at'] = str(product.created_at)
                product_data.append(product_info)
        
        # out of loop test
        # query = f"SELECT * FROM products WHERE product_id = 750706;"
        # product_data = DB_Query(query=query)
        
        return Response({
            "total_favorites": len(product_data),
            "favorites": product_data
        })
        
        
        
        
        
        
        
        
        
        # Get all product_ids from favorites
        # product_ids = [fav.product_id for fav in queryset]
        
        # if not product_ids:
        #     return Response({
        #         "total_favorites": 0,
        #         "favorites": []
        #     })
        
        # # Fetch product details from MySQL for all favorite product_ids
        # product_ids_str = ', '.join(product_ids)
        # query = f"SELECT * FROM products WHERE product_id IN ({product_ids_str});"
        # products_data = DB_Query(query=query)
        # print("----------------------------------------------------")
        # print(products_data)
        # print("----------------------------------------------------")
        
        # # Create a dictionary for quick lookup
        # products_dict = {str(product['product_id']): product for product in products_data}
        
        # # Combine favorite data with product details
        # favorites_with_details = []
        # for favorite in queryset:
        #     product_details = products_dict.get(str(favorite.product_id))
            
        #     favorite_product = product_details if product_details else None
        #     favorite_data = {
        #         "id": favorite.id,
        #         "product_id": favorite.product_id,
        #         "product_name": favorite_product.get("name") if favorite_product else None,
        #         "supermarket_name": favorite_product.get("supermarket_name") if favorite_product else None,
        #         "price": favorite_product.get("price") if favorite_product else None,
        #         "image_url": favorite_product.get("image_url") if favorite_product else None,
        #         "created_at": favorite.created_at,
        #     }
        #     favorites_with_details.append(favorite_data)
        
        # return Response({
        #     "total_favorites": len(products_data),
        #     "favorites": products_data
        # })
            
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
   
















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
class WishlistCreateDeleteView(APIView): 
    permission_classes = [HasActiveSubscription] 

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
    permission_classes = [HasActiveSubscription]

    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user).select_related('product', 'user')


    
    
# create and Delete ShoppingList
class ShoppingListCreateDeleteView(APIView):
    permission_classes = [HasActiveSubscription]

    def post(self, request):
        product_ids = request.data.get("product_ids", [])
        
        if not isinstance(product_ids, list) or not product_ids:
            return Response(
                {"error": "You must provide a list of product_ids."},
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
    permission_classes = [HasActiveSubscription]

    def get_queryset(self):
        return ShoppingList.objects.filter(user=self.request.user).select_related('product', 'user')


    
class ToggleSubscriptionView(APIView):
    permission_classes = [HasActiveSubscription]

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
    permission_classes = [HasActiveSubscription]

    def get_queryset(self):
        return Notification.objects.filter(user=self.request.user).order_by('-created_at')
    
    
class UseNotificationsView(APIView):
    permission_classes = [HasActiveSubscription]

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

class DashboardView(APIView):

    def get(self, request):
        """Retrieve dashboard statistics."""
        total_users = User.objects.count()
        today_new_users = User.objects.filter(create_date=date.today()).count()
        total_products = Product.objects.count()
        total_supermarkets = Supershop.objects.count()

        data = {
            "total_users": total_users,
            "today_new_users": today_new_users,
            "total_products": total_products,
            "total_supermarkets": total_supermarkets,
        }


        return Response(data)


class UsePromoCodeView(APIView):
    def post(self, request):
        serializer = UsePromoCodeSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({"message": "Promo code applied successfully. You are now premium!"})
