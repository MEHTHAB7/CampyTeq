from rest_framework.routers import DefaultRouter
from library.views import BookViewSet, BookIssueViewSet, LibraryRequestViewSet

router = DefaultRouter()
router.register(r"books", BookViewSet, basename="library-books")
router.register(r"issues", BookIssueViewSet, basename="library-issues")
router.register(r"requests", LibraryRequestViewSet, basename="library-requests")

urlpatterns = router.urls
