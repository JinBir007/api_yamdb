from django.contrib.auth import get_user_model
from django.db.models import Avg

from rest_framework import serializers
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator

from ..content.models import Category, Genre, Title
from ..reviews.models import Comment, Review

User = get_user_model()


class ReviewSerializer(ModelSerializer):
    """Сериализатор для модели Review"""
    class Meta:
        model = Review
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=['title', 'author'],
                message='Вы уже оставляли отзыв на данное произведение'
            )
        ]


class CommentSerializer(ModelSerializer):
    """Сериализатор для модели Comment"""
    class Meta:
        model = Comment
        fields = '__all__'


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
        result = Review.objects.filter(title=obj).aggregate(Avg('score'))
        if result['score__avg'] is not None:
            return result['score__avg']
        else:
            return 0
