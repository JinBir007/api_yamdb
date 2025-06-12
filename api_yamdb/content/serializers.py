from rest_framework import serializers
from django.db.models import Avg

from .models import Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""

    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Title."""

    rating = serializers.SerializerMethodField(read_only=True)

    class Meta:
        fields = ('name', 'year', 'rating', 'description', 'genre', 'category')
        model = Title

    def get_rating(self, obj):
        """Функция рассчитывает средний рейтинг из оценок."""
        from reviews.models import Review
        result = Review.objects.filter(title=obj).aggregate(Avg('score'))
        if result['score__avg'] is not None:
            return result['score__avg']
        else:
            return 0
