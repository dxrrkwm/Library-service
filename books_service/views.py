from rest_framework import viewsets
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
