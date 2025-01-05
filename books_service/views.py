from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework_simplejwt.authentication import JWTAuthentication

from books_service.models import Book
from books_service.permissions import IsAdminOrReadOnly
from books_service.serializers import (
    BookDetailSerializer,
    BookListSerializer,
    BookSerializer,
    BookImageSerializer,
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

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image",
        permission_classes=[IsAdminUser],
    )
    def upload_image(self, request, pk=None):
        book = self.get_object()
        serializer = self.get_serializer(book, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_queryset(self):
        title = self.request.query_params.get("title")
        author = self.request.query_params.get("author")

        queryset = self.queryset

        if title:
            queryset = queryset.filter(title__icontains=title)

        if author:
            queryset = queryset.filter(author__icontains=author)

        return queryset.distinct()

    def get_serializer_class(self):
        if self.action == "upload_image":
            return BookImageSerializer

        return self.action_serializer_classes.get(self.action, BookSerializer)
