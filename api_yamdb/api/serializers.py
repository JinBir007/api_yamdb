from django.contrib.auth import get_user_model
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator

from ..reviews.models import Review, Comment

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
