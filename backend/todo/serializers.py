from rest_framework import serializers
from .models import Task, Category
from .tasks import notify_task_due

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "all"

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "all"

    def perform_create(self, serializer):
        task = serializer.save(user=self.request.user)
        notify_task_due.apply_async(args=[task.id], eta=task.due_date)
        