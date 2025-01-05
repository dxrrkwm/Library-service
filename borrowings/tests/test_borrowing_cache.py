import time

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from books_service.models import Book
from borrowings.models import Borrowing

BORROWING_LIST_URL = reverse("borrowings:borrowing-list")
BORROWING_RETURN_URL = reverse("borrowings:return-book", args=[1])


def sample_user(**params):
    defaults = {
        "username": "testuser",
        "password": "password123",
    }
    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


def sample_book(**params):
    defaults = {
        "title": "Book",
        "author": "Author",
        "cover": "hardcover",
        "inventory": 10,
        "daily_fee": 3.00,
    }
    defaults.update(params)
    return Book.objects.create(**defaults)


def sample_borrowing(user, book, **params):
    defaults = {
        "book": book,
        "user": user,
        "borrow_date": now(),
        "due_date": now() + timedelta(days=7),
    }
    defaults.update(params)
    return Borrowing.objects.create(**defaults)


class BorrowingCacheTests(TestCase):
    def setUp(self):
        # Clear the cache before each test
        cache.clear()

        # Create test users and books
        self.user = sample_user(username="testuser", password="password123")
        self.book = sample_book(title="Sample Book")
        self.borrowing = sample_borrowing(user=self.user, book=self.book)

        # Set the authentication token for the user
        self.client.force_authenticate(user=self.user)

    def test_list_borrowings_caches_data(self):
        # Send the first request: it should cache the result
        response = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the response data has been cached
        cache_key = f"borrowing_list_{self.user.id}_None"  # as no 'is_active' filter is provided
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)

    def test_cached_data_is_returned_on_subsequent_requests(self):
        # First request to cache the data
        self.client.get(BORROWING_LIST_URL)

        # Wait for a moment to ensure the cache hasn't expired
        time.sleep(1)

        # Second request should return cached data
        response = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the cached data is returned
        cache_key = f"borrowing_list_{self.user.id}_None"
        cached_data = cache.get(cache_key)
        self.assertEqual(cached_data, response.data)

    def test_cache_expires_after_15_minutes(self):
        # First request to cache the data
        self.client.get(BORROWING_LIST_URL)

        # Wait for 15 minutes to ensure the cache expires
        time.sleep(900)

        # Send another request after 15 minutes
        response = self.client.get(BORROWING_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Ensure that the cache has been refreshed
        cache_key = f"borrowing_list_{self.user.id}_None"
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)

    def test_return_book_updates_inventory(self):
        # Create borrowing for the book
        borrowing = sample_borrowing(user=self.user, book=self.book)

        # Request to return the book
        response = self.client.post(BORROWING_RETURN_URL, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the book's inventory was updated
        self.book.refresh_from_db()
        self.assertEqual(self.book.inventory, 11)  # Book's inventory should increase by 1

        # Ensure the actual return date is set
        borrowing.refresh_from_db()
        self.assertIsNotNone(borrowing.actual_return_date)
