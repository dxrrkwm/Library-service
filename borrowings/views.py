from django.core.cache import cache
from django.db import transaction
from django.utils.decorators import method_decorator
from django.utils.timezone import now
from django.views.decorators.cache import cache_page
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingDetailSerializer,
    BorrowingListSerializer,
    BorrowingSerializer,
)


class BorrowingListView(generics.ListCreateAPIView):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingListSerializer

    def perform_create(self, serializer):
        book = serializer.validated_data["book"]
        if book.inventory <= 0:
            raise ValidationError({"error": "The book is not available for borrowing."})
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

    def get_serializer_class(self):
        if self.request.method == "GET":
            return BorrowingListSerializer
        return BorrowingSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "user",
                type={"type": "list", "items": {"type": "number"}},
                description="Filter by user id (ex. ?user=2,5)",
            ),
            OpenApiParameter(
                "is_active",
                type={"type": "bool", "items": {"type": "number"}},
                description="Filter by user is active "
                            "(ex. ?is_active=1 or 0)",
            ),
        ]
    )
    @method_decorator(cache_page(60 * 15))
    def list(self, request, *args, **kwargs):
        user = request.query_params.get("user")
        is_active = request.query_params.get("is_active")

        cache_key = f"borrowing_list_{user}_{is_active}"
        cached_data = cache.get(cache_key)

        if cached_data:
            return Response(cached_data)

        response = super().list(request, *args, **kwargs)
        cache.set(cache_key, response.data, 900)

        return response


class BorrowingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Borrowing.objects.select_related("book", "user")
    serializer_class = BorrowingDetailSerializer


class ReturnBookView(APIView):
    def post(self, request, pk):
        try:
            borrowing = Borrowing.objects.get(pk=pk)
        except Borrowing.DoesNotExist as err:
            raise ValidationError({"error": "Borrowing not found."}) from err

        if borrowing.actual_return_date:
            raise ValidationError({"error": "The book has already been returned."})

        with transaction.atomic():
            borrowing.actual_return_date = now().date()
            borrowing.book.inventory += 1
            borrowing.book.save()
            borrowing.save()

        return Response(
            {"message": "The book has been successfully returned."},
            status=status.HTTP_200_OK
        )
