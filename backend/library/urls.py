from rest_framework.routers import DefaultRouter
from library.views import BookViewSet, BookIssueViewSet

router = DefaultRouter()
router.register(r"books", BookViewSet, basename="library-books")
router.register(r"issues", BookIssueViewSet, basename="library-issues")

urlpatterns = router.urls
