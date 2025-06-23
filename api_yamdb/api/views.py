from django.db.models import Avg
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, DestroyModelMixin)
from rest_framework.pagination import (
    LimitOffsetPagination, PageNumberPagination)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .filters import TitleFilter
from .permissions import (
    IsAdminOrReadOnly,
    IsAuthorOrModeratorOrAdminOrReadOnly,
    OnlyAdminHasAccess,
)
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    ConfirmationSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    UserRegistrationSerializer,
    UsersMePatchSerializer,
    UsersSerializer,
)
from reviews.models import Category, Genre, Title, Review

User = get_user_model()


class ReviewViewSet(ModelViewSet):
    """Представление отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_title(self):
        """Получение объекта произведения."""""
        return get_object_or_404(Title, id=self.kwargs.get('title_id'))

    def get_queryset(self):
        """Получение списка отзывов."""
        title = self.get_title()
        return title.review_titles.all()

    def perform_create(self, serializer):
        """Создание нового отзыва."""
        serializer.save(author=self.request.user, title=self.get_title())


class CommentViewSet(ModelViewSet):
    """Представление комментариев."""

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_review(self):
        """Получение объекта отзыва."""
        review = self.kwargs.get('review_id')
        title = self.kwargs.get('title_id')
        return get_object_or_404(Review, id=review, title_id=title)

    def get_queryset(self):
        """Получение списка комментариев."""
        review = self.get_review()
        return review.comments.all()

    def perform_create(self, serializer):
        """Создание нового комментария."""
        review = self.get_review()
        serializer.save(
            author=self.request.user,
            review=review,
            title=review.title
        )


class UserRegistrationViewSet(CreateModelMixin,
                              GenericViewSet):
    """Регистрация новых пользователей."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_200_OK, headers=headers)


class RegistrationConfirmation(APIView):
    """Подтверждение электронной почты."""

    def post(self, request):
        serializer = ConfirmationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = request.data.get('username')
        user = get_object_or_404(User, username=username)
        user.email_confirmed = True
        user.save()
        access_token = AccessToken.for_user(user)
        return Response({'token': str(access_token)},
                        status=HTTP_200_OK)


class UserViewSet(ModelViewSet):
    """Обработка прочих эндпойнтов users."""

    queryset = User.objects.all()
    serializer_class = UsersSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')
    lookup_field = 'username'
    permission_classes = (OnlyAdminHasAccess,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    pagination_class = PageNumberPagination

    @action(detail=False,
            methods=('get', 'patch',),
            url_name='me',
            permission_classes=(IsAuthenticated,),
            serializer_class=UsersMePatchSerializer)
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        serializer = self.get_serializer(user,
                                         data=request.data,
                                         partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class BaseViewSet(CreateModelMixin,
                  ListModelMixin,
                  DestroyModelMixin,
                  GenericViewSet):
    """Базовый ViewSet для моделей с полями name и slug."""

    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter, OrderingFilter]
    search_fields = ['name']
    ordering = ['name']
    lookup_field = 'slug'


class CategoryViewSet(BaseViewSet):
    """ViewSet для модели Category."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(BaseViewSet):
    """ViewSet для модели Genre."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(ModelViewSet):
    """ViewSet для модели Title."""

    queryset = Title.objects.annotate(
        rating=Avg('review_titles__score')
    ).all()
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAdminOrReadOnly]
    http_method_names = ('get', 'post', 'patch', 'delete')
    filter_backends = [
        DjangoFilterBackend,
        SearchFilter,
        OrderingFilter
    ]
    filterset_class = TitleFilter
    search_fields = ['name']
    ordering_fields = ['name', 'year']

    def get_serializer_class(self):
        """Возвращает сериализатор в зависимости от действия."""
        if self.action in ['list', 'retrieve']:
            return TitleReadSerializer
        return TitleWriteSerializer
