from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (
    CreateModelMixin, RetrieveModelMixin, UpdateModelMixin)
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK
from rest_framework.views import APIView
from rest_framework.viewsets import (
    ModelViewSet, GenericViewSet, ReadOnlyModelViewSet)
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import ReviewSerializer, CommentSerializer
from reviews.models import Review, Comment
from users.models import EmailConfirmation
from .serializers import (ConfirmationSerializer,
                          UserRegistrationSerializer,
                          UsersMePatchSerializer,
                          UsersSerializer, CategorySerializer,
                          GenreSerializer, TitleSerializer)
from .utils import send_confirmation_email
from .exceptions import WrongUsernameOrToken
from content.models import Genre, Category, Title
from .permissions import (IsAdminOrReadOnly,
                          IsUserOrModeratorOrReadOnly,
                          OnlyAdminHasAccess)

User = get_user_model()


class ReviewViewSet(ModelViewSet):
    """ViewSet для модели Review"""""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')


class CommentViewSet(ModelViewSet):
    """ViewSet для модели Comment"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    http_method_names = ('get', 'post', 'patch', 'delete')


# раздел классов для работы с пользователями

class UserRegistrationViewSet(CreateModelMixin,
                              GenericViewSet):
    """Регистрация новых пользователей."""

    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def create(self, request, *args, **kwargs):
        username = request.data.get('username')
        try:
            user = User.objects.get(username=username,
                                    email_confirmed=False)
            user.delete()
        except Exception:
            pass
        return super().create(request, *args, **kwargs)

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
                raise WrongUsernameOrToken
            user.email_confirmed = True
            user.save()
            refresh = RefreshToken.for_user(user)
            return Response({'token': str(refresh.access_token)},
                            status=HTTP_200_OK)


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
    lookup_field = 'username'
    permission_classes = (OnlyAdminHasAccess,)
    filter_backends = (SearchFilter,)
    search_fields = ('username',)
    pagination_class = LimitOffsetPagination

# конец раздела классов для работы с пользователями


class CategoryViewSet(ReadOnlyModelViewSet):
    """ViewSet для модели Category."""""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class GenreViewSet(ReadOnlyModelViewSet):
    """ViewSet для модели Genre."""""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class TitleViewSet(ModelViewSet):
    """ViewSet для модели Title."""""

    queryset = Title.objects.all()
    serializer_class = TitleSerializer
    pagination_class = LimitOffsetPagination
