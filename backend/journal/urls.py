from rest_framework.routers import DefaultRouter
from .views import TagViewSet, EntryViewSet

router = DefaultRouter()
router.register(r"tags", TagViewSet, basename="tag")
router.register(r"entries", EntryViewSet, basename="entry")

urlpatterns = router.urls