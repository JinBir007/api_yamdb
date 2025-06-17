from django.contrib.auth import get_user_model
# from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.db.models import Avg

from rest_framework.serializers import (
    ModelSerializer, ValidationError, SlugRelatedField, CharField, Serializer,
    SerializerMethodField)
from rest_framework.validators import UniqueTogetherValidator

from reviews.models import Review, Comment
from content.models import Genre, Title, Category
import logging
logger = logging.getLogger(__name__)

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
    category = SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
        write_only=True
    )
    genre = SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field='slug',
        write_only=True
    )
    category_data = CategorySerializer(source='category', read_only=True)
    genre_data = GenreSerializer(source='genre', many=True, read_only=True)

    class Meta:
        model = Title
        fields = ['id', 'name', 'year', 'description', 'genre', 'genre_data', 'category', 'category_data', 'rating']
        read_only_fields = ['rating', 'genre_data', 'category_data']

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        category_data = representation.pop('category_data', None)
        if category_data:
            representation['category'] = category_data

        genre_data = representation.pop('genre_data', None)
        if genre_data:
            representation['genre'] = genre_data
        return representation

    def get_rating(self, obj):
        """Функция рассчитывает средний рейтинг из оценок."""
        result = Review.objects.filter(title_id=obj.id).aggregate(Avg('score'))
        if result['score__avg'] is not None:
            return result['score__avg']
        else:
            return None

    def create(self, validated_data):
        genres = validated_data.pop('genre', [])
        title = Title.objects.create(**validated_data)
        title.genre.set(genres)
        return title
