from django.urls import path

from .views import BorrowingDetailView, BorrowingListView, ReturnBookView

urlpatterns = [
    path("", BorrowingListView.as_view(), name="borrowing-list"),
    path("<int:pk>/", BorrowingDetailView.as_view(), name="borrowing-detail"),
    path("<int:pk>/return/", ReturnBookView.as_view(), name="return-book"),
]

app_name = "borrowings"
