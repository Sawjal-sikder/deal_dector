from rest_framework.views import APIView # type: ignore
from rest_framework.response import Response # type: ignore
from rest_framework import permissions # type: ignore
from ..models import NotificationProducts # type: ignore
from service.views.products_views import get_all_products_cached # type: ignore



class NotificationView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        notifications = NotificationProducts.objects.filter(user=user).values('id', 'product_id', 'created_at')
        all_products = get_all_products_cached()
        
        result = []
        for notification in notifications:
            product = next((p for p in all_products if p.get('id') == notification['product_id']), None)
            if product and product.get('discount_label'):
                result.append({
                    'id': notification['id'],
                    'product_id': notification['product_id'],
                    "offer_name": f"{product.get('name')} offer!",
                    'product_discount_contain': product.get('discount_label'),
                })

        return Response({'notifications': result})