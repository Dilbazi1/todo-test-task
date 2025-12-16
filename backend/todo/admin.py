
from django.contrib import admin
from .models import Task, Category

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "category", "due_date", "created_at", "is_done")
    list_filter = ("is_done", "category")
    search_fields = ("title", "description")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user")
    search_fields = ("name",)
