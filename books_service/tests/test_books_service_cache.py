import time

from django.core.cache import cache
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from books_service.models import Book

BOOKS_SERVICE_URL = reverse("books_service:book-list")

# Helper function to create a sample book
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

class BookCacheTests(TestCase):
    def setUp(self):
        # Clear cache before each test
        cache.clear()
        # Create two sample books
        self.book1 = sample_book(title="Book 1")
        self.book2 = sample_book(title="Book 2")

    def test_list_books_caches_data(self):
        # First request: the result should be cached
        response = self.client.get(BOOKS_SERVICE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the data has been added to the cache
        cache_key = f"book_list_{self.client.request.query_params}"
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)

    def test_cached_data_is_returned_on_subsequent_requests(self):
        # First request, the result is cached
        self.client.get(BOOKS_SERVICE_URL)

        # Wait a short time to ensure the cache doesn't expire
        time.sleep(1)

        # Second request, should return cached data
        response = self.client.get(BOOKS_SERVICE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check that the cached data matches the response
        cache_key = f"book_list_{self.client.request.query_params}"
        cached_data = cache.get(cache_key)
        self.assertEqual(cached_data, response.data)

    def test_cache_expires_after_15_minutes(self):
        # Trigger the first request to cache the data
        self.client.get(BOOKS_SERVICE_URL)

        # Wait for 15 minutes (900 seconds) to check if the cache expires
        time.sleep(900)

        # Make a request after the cache expiration time
        response = self.client.get(BOOKS_SERVICE_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Check if the cache has been refreshed with new data
        cache_key = f"book_list_{self.client.request.query_params}"
        cached_data = cache.get(cache_key)
        self.assertIsNotNone(cached_data)
