from rest_framework import viewsets

from books_service.models import Book
from books_service.serializers import (
    BookDetailSerializer,
    BookListSerializer,
    BookSerializer,
)


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()

    action_serializer_classes = {
        "list": BookListSerializer,
        "retrieve": BookDetailSerializer,
        "create": BookSerializer,
        "update": BookSerializer,
        "partial_update": BookSerializer
    }

    def get_serializer_class(self):
        return self.action_serializer_classes.get(self.action, BookSerializer)
