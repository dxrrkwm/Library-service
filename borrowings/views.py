from django.utils.timezone import now
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Borrowing
from .serializers import (
    BorrowingDetailSerializer,
    BorrowingSerializer,
)


class BorrowingListView(generics.ListCreateAPIView):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingSerializer

    def perform_create(self, serializer):
        book = serializer.validated_data["book"]
        if book.inventory <= 0:
            return Response(
                {"error": "The book is not available for borrowing."},
                status=status.HTTP_400_BAD_REQUEST
            )
        book.inventory -= 1
        book.save()
        serializer.save()

    @staticmethod
    def _params_to_ints(params):
        return [int(str_id) for str_id in params.split(",")]

    def get_queryset(self):
        user = self.request.query_params.get("user")
        is_active = self.request.query_params.get("is_active")

        queryset = self.queryset

        if is_active:
            queryset = queryset.filter(user__is_active=is_active)

        if user:
            user_ids = self._params_to_ints(user)
            queryset = queryset.filter(user_id__in=user_ids)

        return queryset.distinct()

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "user",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by user id (ex. ?user=2,5)",
            ),
            OpenApiParameter(
                "is_active",
                type={"type": "integer", "items": {"type": "number"}},
                description="Filter by user is activ "
                            "(ex. ?is_activ=1 or 0)",
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class BorrowingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingDetailSerializer


class ReturnBookView(APIView):
    def post(self, request, pk):
        try:
            borrowing = Borrowing.objects.get(pk=pk)
        except Borrowing.DoesNotExist:
            return Response(
                {"error": "Borrowing not found."},
                status=status.HTTP_404_NOT_FOUND,
            )

        if borrowing.actual_return_date:
            return Response(
                {"error": "The book has already been returned."},
                status=status.HTTP_400_BAD_REQUEST
            )
        borrowing.actual_return_date = now().date()
        borrowing.book.inventory += 1
        borrowing.book.save()
        borrowing.save()
        return Response(
            {"message": "The book has been successfully returned."},
            status=status.HTTP_200_OK
        )
