from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model

from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.mixins import (
    CreateModelMixin, RetrieveModelMixin, UpdateModelMixin)
from rest_framework.response import Response
from rest_framework.pagination import (LimitOffsetPagination,
                                       PageNumberPagination)
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_405_METHOD_NOT_ALLOWED
from rest_framework.views import APIView
from rest_framework.viewsets import (
    ModelViewSet, GenericViewSet, ReadOnlyModelViewSet)
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.exceptions import MethodNotAllowed
from rest_framework import viewsets, mixins

from .serializers import ReviewSerializer, CommentSerializer
from reviews.models import Review, Comment
from users.models import EmailConfirmation
from .serializers import (ConfirmationSerializer,
                          UserRegistrationSerializer,
                          UsersMePatchSerializer,
                          UsersSerializer, CategorySerializer,
                          GenreSerializer, TitleSerializer)
from .utils import send_confirmation_email
from .exceptions import WrongEmail, WrongUsernameOrCode
from content.models import Genre, Category, Title
from .permissions import (IsAdminOrReadOnly,
                          IsUserOrModeratorOrReadOnly,
                          OnlyAdminHasAccess)

User = get_user_model()


class ReviewViewSet(viewsets.ModelViewSet):
    """Представление отзывов."""
    serializer_class = ReviewSerializer
    permission_classes = (IsUserOrModeratorOrReadOnly,)
    pagination_class = PageNumberPagination
    http_method_names = ('get', 'post', 'patch', 'delete')

    def perform_create(self, serializer):
        title = get_object_or_404(
            Title,
            pk=self.kwargs.get('title_id')
        )
        serializer.save(
            author=self.request.user,
            title=title
        )

    def get_queryset(self):
        title = self.kwargs.get('title_id')
        return Review.objects.filter(id=title)


class CommentViewSet(viewsets.ModelViewSet):
    """Представление комментариев."""
    serializer_class = CommentSerializer
    permission_classes = (IsUserOrModeratorOrReadOnly,)
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


# раздел классов для работы с пользователями

class UserRegistrationViewSet(CreateModelMixin,
                              GenericViewSet):
    """Регистрация новых пользователей."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        email = request.data.get('email')
        if User.objects.filter(username=username,
                               email_confirmed=False).exists():
            user = User.objects.get(username=username,
                                    email_confirmed=False)
            if user.email != email:
                raise WrongEmail('Указан некорректный адрес электроннной почты')
            user.delete()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=HTTP_200_OK, headers=headers)

    def perform_create(self, serializer):
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        if not User.objects.filter(username=username).exists():
            serializer.save()
        user = get_object_or_404(User, username=username)
        try:
            confirmation = EmailConfirmation.objects.get(user=user)
            confirmation.delete()
        except Exception:
            pass
        confirmation_object = EmailConfirmation.objects.create(
            user=user)
        confirmation_code = confirmation_object.id
        send_confirmation_email(user, confirmation_code, email)


class RegistrationConfirmation(APIView):
    """Подтверждение электронной почты."""

    def post(self, request):
        serializer = ConfirmationSerializer(data=request.data)
        if serializer.is_valid():
            username = request.data.get('username')
            user = get_object_or_404(User, username=username)
            user_confirmation_code = request.data.get('confirmation_code')
            try:
                confirmation = EmailConfirmation.objects.get(
                    pk=user_confirmation_code,
                    user=user
                )
            except Exception:
                raise WrongUsernameOrCode
            user.email_confirmed = True
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({'token': str(refresh.access_token)},
                            status=HTTP_200_OK)
        else:
            raise WrongUsernameOrCode


class UsersMeViewSet(GenericViewSet,
                     UpdateModelMixin,
                     RetrieveModelMixin):
    """Получение и изменение информации о текущем пользователе."""

    queryset = User.objects.all()
    serializer_class = UsersSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.pk)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UsersSerializer
        else:
            return UsersMePatchSerializer


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

    def _allowed_methods(self):
        methods = [m.upper() for m in
                   self.http_method_names if hasattr(self, m)]
        print(self.detail)
        if self.detail and 'POST' in methods:
            methods.remove('POST')
        return methods

# конец раздела классов для работы с пользователями


class CategoryViewSet(ModelViewSet):
    """ViewSet для модели Category."""""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def retrieve(self, request, *args, **kwargs):
        raise MethodNotAllowed('GET')

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')


class GenreViewSet(ModelViewSet):
    """ViewSet для модели Genre."""""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    lookup_field = 'slug'
    permission_classes = [IsAdminOrReadOnly]
    filter_backends = [SearchFilter]
    search_fields = ['name']

    def retrieve(self, request, *args, **kwargs):
        raise MethodNotAllowed('GET')

    def partial_update(self, request, *args, **kwargs):
        raise MethodNotAllowed('PATCH')


class TitleViewSet(ModelViewSet):
    """ViewSet для модели Title."""

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['name']
    ordering_fields = ['name', 'year']

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            genre = self.request.query_params.get('genre', None)
            category = self.request.query_params.get('category', None)
            year = self.request.query_params.get('year', None)
            name = self.request.query_params.get('name', None)

            if genre is not None:
                queryset = queryset.filter(genre__slug=genre)
            if category is not None:
                queryset = queryset.filter(category__slug=category)
            if year is not None:
                queryset = queryset.filter(year=year)
            if name is not None:
                queryset = queryset.filter(name=name)
        return queryset

    def update(self, request, *args, **kwargs):
        """Запрещает PUT-запросы (полное обновление)."""
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def partial_update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data)

    def perform_update(self, serializer):
        serializer.save()
