from re import sub

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django.db.models import Avg

from rest_framework.serializers import (
    CharField,
    EmailField,
    ModelSerializer,
    Serializer,
    SerializerMethodField,
    SlugRelatedField,
    ValidationError,
)

from reviews.models import Category, Genre, Title, Comment, Review
from users.constants import (FORBIDDEN_SYMBOLS,
                             MAX_USERNAME_LENGTH,
                             MAX_EMAIL_LENGTH)
from .utils import send_confirmation_email

User = get_user_model()


class ReviewSerializer(ModelSerializer):
    """Сериализатор отзывов."""

    author = SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Review
        fields = ('id', 'author', 'text', 'score', 'pub_date')

    def validate(self, attrs):
        """Проверка на повторный отзыв"""
        request = self.context.get('request')
        if Review.objects.filter(
            author=request.user,
            title_id=self.context.get('view').kwargs.get('title_id')
        ).exists() and request.method == 'POST':
            raise ValidationError(
                'Нельзя создать повторный отзыв на это произведение')
        return attrs


class CommentSerializer(ModelSerializer):
    """Сериализатор комментариев."""

    author = SlugRelatedField(
        read_only=True,
        slug_field='username'
    )

    class Meta:
        model = Comment
        fields = ('id', 'text', 'author', 'pub_date',)


# раздел сериализаторов для классов работы с пользователями

class UserRegistrationSerializer(Serializer):
    username = CharField(max_length=MAX_USERNAME_LENGTH, allow_blank=False)
    email = EmailField(max_length=MAX_EMAIL_LENGTH, allow_blank=False)

    def validate_username(self, value):
        if value == 'me':
            raise ValidationError(
                {'username': ('Недопустимое значение.',)}
            )
        incorrect_entries = sub(FORBIDDEN_SYMBOLS, '', value)
        if len(incorrect_entries) > 0:
            raise ValidationError(f'Недопустимые символы {incorrect_entries}')
        return value

    def create(self, validated_data):
        username = validated_data.get('username')
        email = validated_data.get('email')
        try:
            user, _ = User.objects.get_or_create(username=username,
                                                 email=email,
                                                 email_confirmed=False)
        except IntegrityError:
            raise ValidationError('Имя пользователя либо адрес '
                                  'электронной почты уже используются.')
        confirmation_token = default_token_generator.make_token(user)
        send_confirmation_email(user, confirmation_token, email)
        return user


class ConfirmationSerializer(Serializer):
    username = CharField(max_length=MAX_USERNAME_LENGTH, allow_blank=False)
    confirmation_code = CharField(allow_blank=False)


class UsersSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ('username',
                  'email',
                  'first_name',
                  'last_name',
                  'bio',
                  'role')


class UsersMePatchSerializer(UsersSerializer):
    class Meta(UsersSerializer.Meta):
        read_only_fields = ('role',)


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
        fields = [
            'id', 'name', 'year', 'description', 'genre', 'genre_data',
            'category', 'category_data', 'rating'
        ]
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
