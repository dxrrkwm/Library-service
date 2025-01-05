from django.contrib import admin
from borrowings.models import Borrowing

@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = ("user", "book", "borrow_date", "actual_return_date", "expected_return_date")
    search_fields = ("user__last_name", "user__email", "book__title")
    list_filter = ("borrow_date", "actual_return_date", "expected_return_date")
    ordering = ("-borrow_date",)
