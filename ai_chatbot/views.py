# chats/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import *
from .models import *
from .main import main  

class ChatHistoryView(APIView):
    serializer_class = ChatHistorySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            # Extract user input
            request_data = serializer.validated_data.get("request_data")

            # Call Celery task asynchronously
            task_result = main.delay(request_data)

            try:
                # Wait for the result with a timeout
                response_data = task_result.get(timeout=600)

                # Save chat history
                chat = ChatHistory.objects.create(
                    user=request.user,
                    flag=response_data.get("flag"),
                    request_data=request_data,
                    response_data=response_data,
                )

                return Response(
                    self.serializer_class(chat).data,
                    status=status.HTTP_201_CREATED,
                )

            except Exception as e:
                return Response(
                    {"error": f"Task execution failed: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChatHistoryListView(APIView):
    def get(self, request):
        chats = ChatHistory.objects.all()#.order_by('-created_at')
        serializer = ChatHistoryListSerializer(chats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
  
class RecipeListView(APIView):
      def get(self, request):
          recipes = ChatHistory.objects.filter(user=request.user, flag="list_generated").order_by('-created_at')
          serializer = RecipeListSerializer(recipes, many=True)
          return Response(serializer.data, status=status.HTTP_200_OK)