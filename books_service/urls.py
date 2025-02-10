from rest_framework.routers import DefaultRouter

from books_service.views import BookViewSet

app_name = "books_service"

router = DefaultRouter()
router.register("books", BookViewSet)

urlpatterns = router.urls
