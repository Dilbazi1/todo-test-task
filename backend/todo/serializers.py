
from rest_framework import serializers
from .models import Task, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ("id", "name")
        read_only_fields = ("id",)


class TaskSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.CharField(write_only=True, required=False)

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
            validated_data["category"] = Category.objects.get(
                id=category_id,
                user=self.context["request"].user
            )

        return Task.objects.create(
            user=self.context["request"].user,
            **validated_data
        )