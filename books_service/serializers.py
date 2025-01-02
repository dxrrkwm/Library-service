from rest_framework import serializers

from books_service.models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "cover",
            "inventory",
            "daily_fee"
        )


class BookListSerializer(BookSerializer):
    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author"
        )


class BookDetailSerializer(BookSerializer):
    cover_display = serializers.CharField(source="get_cover_display")
    total_value = serializers.SerializerMethodField()

    class Meta:
        model = Book
        fields = (
            "id",
            "title",
            "author",
            "cover",
            "cover_display",
            "inventory",
            "daily_fee",
            "total_value"
        )
        read_only_fields = ("cover_display", "total_value")

    def get_total_value(self, obj):
        return obj.inventory * obj.daily_fee
