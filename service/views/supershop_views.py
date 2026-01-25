from rest_framework.response import Response # type: ignore
from rest_framework.views import APIView # type: ignore
from rest_framework import permissions # type: ignore

from service.utils.fetch_mysql_data import DB_Query


class SuperShopMySQLView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        
        query = "SELECT * FROM supermarkets;"
        supermarkets = list(DB_Query(query=query))  

        total_supermarkets = len(supermarkets)
        
        return Response({
            "total_supermarkets": total_supermarkets,
            "supermarkets": supermarkets
        })
