from django.db.models import Avg
from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.shortcuts import get_object_or_404


from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.mixins import (
    CreateModelMixin, ListModelMixin, DestroyModelMixin)
from rest_framework.pagination import (
    LimitOffsetPagination, PageNumberPagination)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from django_filters.rest_framework import DjangoFilterBackend

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
    # TitleSerializer,
    TitleReadSerializer,
    TitleWriteSerializer,
    UserRegistrationSerializer,
    UsersMePatchSerializer,
    UsersSerializer,
)
from reviews.models import Category, Genre, Title, Review

User = get_user_model()


class ReviewViewSet(viewsets.ModelViewSet):
    """Представление отзывов."""

    serializer_class = ReviewSerializer
    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,)
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        title_id = self.kwargs.get('title_id')
        return Review.objects.filter(title_id=title_id)

    def perform_create(self, serializer):
        title_id = self.kwargs.get('title_id')
        title = get_object_or_404(Title, id=title_id)
        serializer.save(author=self.request.user, title=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Представление комментариев."""

    serializer_class = CommentSerializer
    permission_classes = (IsAuthorOrModeratorOrAdminOrReadOnly,)
    http_method_names = ('get', 'post', 'patch', 'delete')

    def get_queryset(self):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id')
        )
        return review.comments.all().order_by('id')

    def perform_create(self, serializer):
        review = get_object_or_404(
            Review,
            pk=self.kwargs.get('review_id')
        )
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id')
        )
        serializer.save(
            title=title,
            author=self.request.user,
            review=review,
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
        if serializer.is_valid():
            username = request.data.get('username')
            user = get_object_or_404(User, username=username)
            confirmation_code = request.data.get('confirmation_code')
            if default_token_generator.check_token(user, confirmation_code):
                user.email_confirmed = True
                user.save()
                access_token = AccessToken.for_user(user)
                return Response({'token': str(access_token)},
                                status=HTTP_200_OK)
            else:
                return Response('Указаны некорректные данные',
                                status=HTTP_400_BAD_REQUEST)
        else:
            return Response('Указаны некорректные данные',
                            status=HTTP_400_BAD_REQUEST)


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

    def get_permissions(self):
        if self.action == 'me':
            return (IsAuthenticated(),)
        return (OnlyAdminHasAccess(),)

    def get_serializer_class(self):
        if self.action == 'me':
            return UsersMePatchSerializer
        else:
            return UsersSerializer

    @action(detail=False,
            methods=('get', 'patch', 'put', 'delete'),
            url_name='me')
    def me(self, request):
        user = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(user)
            return Response(serializer.data)
        elif request.method == 'PATCH':
            serializer = self.get_serializer(user,
                                             data=request.data,
                                             partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
        else:
            raise MethodNotAllowed(f'{request.method}')


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
