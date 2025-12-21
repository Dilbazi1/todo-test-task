
from rest_framework import serializers
from backend.todo.models import Task, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")
        read_only_fields = ("id",)


class TaskSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.CharField(write_only=True, required=False, allow_blank=True)

    class Meta:
        model = Task
        fields = (
            "id",
            "title",
            "description",
            "category",
            "category_id",
            "due_date",
            "created_at",
            "is_done",
        )
        read_only_fields = ("id", "created_at")


  
    def create(self, validated_data):
        category_id = validated_data.pop("category_id", None)

        if category_id:
            try:
                validated_data["category"] = Category.objects.get(
                    id=category_id,
                    user=self.context["request"].user
                )
            except Category.DoesNotExist:
                raise serializers.ValidationError(
                    {"category_id": "Категория не найдена"}
                )

        return Task.objects.create(
            user=self.context["request"].user,
            **validated_data
        )
    def validate(self, attrs):
        due_date = attrs.get("due_date")
        created_at = getattr(self.instance, "created_at", None)

        # При обновлении
        if self.instance and due_date and created_at:
            if due_date < created_at:
                raise serializers.ValidationError(
                    {"due_date": "Дедлайн не может быть раньше создания задачи"}
                )

        return attrs