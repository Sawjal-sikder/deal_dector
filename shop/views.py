from rest_framework.parsers import JSONParser, MultiPartParser, FormParser
from rest_framework import generics
from .models import Supershop
from .serializers import SupershopSerializer

class SupershopListCreateView(generics.ListCreateAPIView):
    queryset = Supershop.objects.all()
    serializer_class = SupershopSerializer
    parser_classes = (JSONParser, MultiPartParser, FormParser)