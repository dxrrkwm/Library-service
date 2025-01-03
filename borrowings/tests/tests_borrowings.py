from django.utils.timezone import now
from rest_framework import status
from rest_framework.test import APITestCase

from books_service.models import Book
from borrowings.models import Borrowing
from users.models import User


class ReturnBookViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com", password="password123"
        )
        self.client.force_authenticate(user=self.user)

        self.book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            cover="Hard",
            inventory=5,
            daily_fee=1.50,
        )

        self.borrowing = Borrowing.objects.create(
            user=self.user,
            book=self.book,
            borrow_date=now().date(),
            expected_return_date=now().date(),
        )

        self.return_url = f"/api/borrowings/{self.borrowing.id}/return/"

    def test_successful_return(self):
        response = self.client.post(self.return_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.borrowing.refresh_from_db()
        self.book.refresh_from_db()

        self.assertIsNotNone(self.borrowing.actual_return_date)

        self.assertEqual(self.book.inventory, 6)

        self.assertIn(
            "The book has been successfully returned.",
            response.data["message"]
        )

    def test_already_returned(self):
        self.borrowing.actual_return_date = now().date()
        self.borrowing.save()

        response = self.client.post(self.return_url)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        self.assertIn("The book has already been returned", response.data["error"])

    def test_invalid_borrowing_id(self):
        invalid_url = "/api/borrowings/999/return/"
        response = self.client.post(invalid_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        self.assertIn("Borrowing not found.", response.data["error"])
