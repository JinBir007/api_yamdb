from django.contrib.auth import get_user_model
from django.db.models import Avg
from rest_framework.serializers import (
    ModelSerializer, ValidationError, CharField, Serializer,
    SerializerMethodField)
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Review, Comment
from content.models import Genre, Title, Category

User = get_user_model()


class ReviewSerializer(ModelSerializer):
    """Сериализатор для модели Review"""
    class Meta:
        model = Review
        fields = '__all__'
        validators = [
            UniqueTogetherValidator(
                queryset=Review.objects.all(),
                fields=('title', 'author'),
                message='Вы уже оставляли отзыв на данное произведение'
            )
        ]


class CommentSerializer(ModelSerializer):
    """Сериализатор для модели Comment"""
    class Meta:
        model = Comment
        fields = '__all__'


# раздел сериализаторов для классов работы с пользователями

class UserRegistrationSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError(
                {'username': ('Недопустимое значение.',)}
            )
        return value


class ConfirmationSerializer(Serializer):
    username = CharField(max_length=150, allow_blank=False)
    confirmation_code = CharField(max_length=36, allow_blank=False)


class UsersMePatchSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'bio',)


class UsersSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'bio',
                  'role')

# конец раздела сериализаторов для классов работы с пользователями


class CategorySerializer(ModelSerializer):
    """Сериализатор для модели Category."""

    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(ModelSerializer):
    """Сериализатор для модели Genre."""
    class Meta:
        fields = ('name', 'slug')
        model = Genre



class TitleSerializer(ModelSerializer):
    """Сериализатор для модели Title."""
    rating = SerializerMethodField(read_only=True)
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
