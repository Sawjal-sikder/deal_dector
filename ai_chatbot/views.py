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
                  
                  # Call the Celery task asynchronously
                  task_result = main.delay(recipe_text)
                  
                  try:
                        # Wait for the result with a timeout
                        data = task_result.get(timeout=60)  # 60 seconds timeout
                        return Response(data, status=status.HTTP_200_OK)
                  except Exception as e:
                        return Response(
                              {"error": f"Task execution failed: {str(e)}"}, 
                              status=status.HTTP_500_INTERNAL_SERVER_ERROR
                        )
            return Response(serializers.errors, status=status.HTTP_400_BAD_REQUEST)