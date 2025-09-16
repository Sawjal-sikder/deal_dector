from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from .main import *

# Create your views here.
class GenerateRecipeView(APIView):
      serializer_class = RecipeRequestSerializer

      def post(self, request):
            serializers = self.serializer_class(data=request.data)
            
            if serializers.is_valid():
                  recipe_text = serializers.validated_data["recipe_text"]
                  data = main(recipe_text)
                  return Response(data, status=status.HTTP_200_OK)
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)