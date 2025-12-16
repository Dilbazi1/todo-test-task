
from celery import shared_task
from .models import Task
@shared_task
def notify_task_due(task_id):
    task = Task.objects.get(id=task_id)
    print(f"Task {task.title} is due!")