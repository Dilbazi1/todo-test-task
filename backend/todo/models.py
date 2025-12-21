
from django.db import models
from django.contrib.auth.models import User
from backend.todo.utils import generate_ulid


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True)
    telegram_link_code = models.CharField(
        max_length=10, null=True, blank=True, unique=True
    )

    def str(self):
        return f"{self.user.username} profile"

class Category(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=26,
        default=generate_ulid,
        editable=False
    )
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class Task(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=26,
        default=generate_ulid,
        editable=False
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    due_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_done = models.BooleanField(default=False)
    notified = models.BooleanField(default=False)  
    def __str__(self):
        return self.title
