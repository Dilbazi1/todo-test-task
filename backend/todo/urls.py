from django.urls import path
from rest_framework.routers import DefaultRouter
from backend.todo.views import (
    TaskViewSet,
    CategoryViewSet,
    GetTelegramLinkCodeView,LinkTelegramView
)

router = DefaultRouter()
router.register("tasks", TaskViewSet, basename="task")
router.register("categories", CategoryViewSet, basename="category")

urlpatterns = [
    path(
        "auth/telegram/code/",
        GetTelegramLinkCodeView.as_view(),
        name="telegram-link-code",
    ),
    path("auth/telegram/link/", LinkTelegramView.as_view()),
]

urlpatterns += router.urls