from rest_framework import generics
from .models import Borrowing
from .serializers import (
    BorrowingDetailSerializer,
    BorrowingListSerializer,
)


class BorrowingListView(generics.ListCreateAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingListSerializer

class BorrowingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Borrowing.objects.all()
    serializer_class = BorrowingDetailSerializer
