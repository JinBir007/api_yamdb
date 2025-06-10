from rest_framework.serializers import ModelSerializer
from .models import Review, Comment, Rating


class ReviewSerializer(ModelSerializer):
    """Сериализатор для модели Review"""
    class Meta:
        model = Review
        fields = '__all__'

    def validate(self, attrs):
        """Валидация данных"""
        # TODO: добавить проверку на повторную подписку на основе связей БД
        return attrs


class CommentSerializer(ModelSerializer):
    """Сериализатор для модели Comment"""
    class Meta:
        model = Comment
        fields = '__all__'


class RatingSerializer(ModelSerializer):
    """Сериализатор для модели Rating"""
    class Meta:
        model = Rating
        fields = '__all__'
