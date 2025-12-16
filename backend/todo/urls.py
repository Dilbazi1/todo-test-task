from rest_framework.routers import DefaultRouter
from .views import TaskViewSet, CategoryViewSet

router = DefaultRouter()
router.register("tasks", TaskViewSet)
router.register("categories", CategoryViewSet)

urlpatterns = router.urls




