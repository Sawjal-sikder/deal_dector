from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class ChatHistory(models.Model):
      user = models.ForeignKey(User, on_delete=models.CASCADE)
      flag = models.CharField(max_length=50, blank=True, null=True)
      request_data = models.TextField()
      response_data = models.JSONField() 
      created_at = models.DateTimeField(auto_now_add=True)

      def __str__(self):
            return f"Chat at {self.created_at}"
