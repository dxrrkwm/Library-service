from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from books_service.models import Book
from books_service.permissions import IsAdminOrReadOnly
from books_service.serializers import (
    BookDetailSerializer,
    BookListSerializer,
    BookSerializer,
)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    permission_classes = [IsAdminOrReadOnly]
    authentication_classes = [JWTAuthentication]

    action_serializer_classes = {
        "list": BookListSerializer,
        "retrieve": BookDetailSerializer,
        "create": BookSerializer,
        "update": BookSerializer,
        "partial_update": BookSerializer
    }

    def get_serializer_class(self):
        return self.action_serializer_classes.get(self.action, BookSerializer)

    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        cache_key = f"book_list_{request.query_params}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 900)

        return response

