
from django.db import models
from django.contrib.auth.models import User
from .utils import generate_ulid

class Category(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=26,
        default=generate_ulid,
        editable=False
    )
    name = models.CharField(max_length=100)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

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
