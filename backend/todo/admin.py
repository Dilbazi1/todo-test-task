
from django.contrib import admin
from backend.todo.models import Task, Category,UserProfile

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "category", "due_date", "created_at", "is_done")
    list_filter = ("is_done", "category")
    search_fields = ("title", "description")

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user")
    search_fields = ("name",)

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ("telegram_id", "telegram_link_code","user")
    # search_fields = ("user")