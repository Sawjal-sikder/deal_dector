# chats/views.py
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics
from celery.result import AsyncResult
from rest_framework import status
from .serializers import *
from .main import main  
from .models import *


class ChatHistoryView(APIView):
    serializer_class = ChatHistorySerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)

        if serializer.is_valid():
            request_data = serializer.validated_data.get("request_data")

            # Start Celery task
            task = main.delay(request_data)

            # Create chat history (empty response for now)
            chat = ChatHistory.objects.create(
                user=request.user,
                request_data=request_data,
                response_data={},  
            )

            return Response(
                {
                    "task_id": task.id,
                    "chat_id": chat.id,
                    "message": "Task started. Use task_id to fetch results.",
                },
                status=status.HTTP_202_ACCEPTED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChatResultView(APIView):
    """Fetch task result by task_id"""

    def get(self, request, task_id):
        result = AsyncResult(task_id)

        if result.ready():
            if result.successful():
                data = result.result

                # Update chat history with response
                chat = ChatHistory.objects.filter(user=request.user).last()
                chat.flag = data.get("flag")
                chat.response_data = data
                chat.save()

                return Response({"status": "done", "result": data}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"status": "failed", "error": str(result.result)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response({"status": "pending"}, status=status.HTTP_202_ACCEPTED)
    
    
    
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
      
      
class RecipeDetailView(generics.RetrieveAPIView):
    queryset = ChatHistory.objects.all()
    serializer_class = RecipeListSerializer
    lookup_field = "pk"