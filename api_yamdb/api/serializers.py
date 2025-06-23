from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from rest_framework.fields import IntegerField
from rest_framework.serializers import (
    CharField,
    EmailField,
    ModelSerializer,
    Serializer,
    SlugRelatedField,
    ValidationError,
)

from reviews.models import Category, Genre, Title, Comment, Review
from users.constants import (MAX_USERNAME_LENGTH,
                             MAX_EMAIL_LENGTH)
from users.validators import validate_name
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



class UserRegistrationSerializer(Serializer):
    username = CharField(max_length=MAX_USERNAME_LENGTH,
                         allow_blank=False,
                         validators=(validate_name,))
    email = EmailField(max_length=MAX_EMAIL_LENGTH, allow_blank=False)

    def create(self, validated_data):
        username = validated_data.get('username',)
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

    def validate_confirmation_code(self, value):
        username = self.initial_data.get('username')
        if username is None:
            raise ValidationError('Указаны некорректные данные.')
        user = get_object_or_404(User, username=username)
        if default_token_generator.check_token(user, value):
            return value
        else:
            raise ValidationError('Указаны некорректные данные.')


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


class TitleWriteSerializer(ModelSerializer):
    """Сериализатор для записи (создания и обновления) модели Title."""

    category = SlugRelatedField(
        queryset=Category.objects.all(),
        slug_field='slug',
        write_only=True,
        required=False
    )
    genre = SlugRelatedField(
        many=True,
        queryset=Genre.objects.all(),
        slug_field='slug',
        write_only=True,
        allow_null=False,
        allow_empty=False,
    )

    class Meta:
        model = Title
        fields = ['id', 'name', 'year', 'description', 'genre', 'category']

    def to_representation(self, instance):
        """Преобразует объект в представление для чтения."""
        return TitleReadSerializer(instance, context=self.context).data


class TitleReadSerializer(ModelSerializer):
    """Сериализатор для чтения (получения) модели Title."""

    rating = IntegerField(read_only=True, default=None)
    category = CategorySerializer(read_only=True)
    genre = GenreSerializer(many=True, read_only=True)

    class Meta:
        model = Title
        fields = [
            'id', 'name', 'year', 'description', 'genre', 'category', 'rating'
        ]
