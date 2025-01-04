from django.urls import path

from borrowings.views import BorrowingDetailView, BorrowingListView, ReturnBookView

urlpatterns = [
    path("", BorrowingListView.as_view(), name="borrowings-list"),
    path("<int:pk>/", BorrowingDetailView.as_view(), name="borrowing-detail"),
    path("<int:pk>/return/", ReturnBookView.as_view(), name="return-book"),
]

app_name = "borrowings"
