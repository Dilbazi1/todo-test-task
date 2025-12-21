

from rest_framework.viewsets import ModelViewSet
from backend.todo.models import Task, Category,UserProfile
from backend.todo.serializers import TaskSerializer, CategorySerializer
import secrets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated,AllowAny
from rest_framework.response import Response
from django.contrib.auth import get_user_model

User = get_user_model()

class GetTelegramLinkCodeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        code = secrets.token_hex(3).upper()

        profile, _ = UserProfile.objects.get_or_create(user=request.user)
        profile.telegram_link_code = code
        profile.save()

        return Response({
            "code": code,
            "telegram_link": f"https://t.me/Todotasktest_bot?start={code}"
        })
class CategoryViewSet(ModelViewSet):
    serializer_class = CategorySerializer

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TaskViewSet(ModelViewSet):
    serializer_class = TaskSerializer

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user).select_related("category")

from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

@method_decorator(csrf_exempt, name='dispatch')
class LinkTelegramView(APIView):
    # authentication_classes = []  # можно добавить токен, если хочешь
    permission_classes=[AllowAny]
    def post(self, request):
        telegram_id = request.data.get("telegram_id")
        code = request.data.get("code")

        if not telegram_id or not code:
            return Response(
                {"error": "telegram_id and code required"},
                status=400
            )

        profile = UserProfile.objects.filter(
            telegram_link_code=code
        ).first()

        if not profile:
            return Response(
                {"error": "Invalid or expired code"},
                status=400
            )

        profile.telegram_id = telegram_id
        profile.telegram_link_code = None
        profile.save()

        return Response({"status": "linked"})