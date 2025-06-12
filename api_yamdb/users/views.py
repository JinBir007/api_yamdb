"""users/views.py

Viewsets для приложения users.
"""

from rest_framework import filters, mixins, permissions, status, viewsets
from rest_framework.response import Response
from rest_framework.pagination import LimitOffsetPagination
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .exceptions import WrongUsernameOrToken
from .models import EmailConfirmation
from .serializers import (ConfirmationSerializer,
                          UserRegistrationSerializer,
                          UsersMeGetSerializer,
                          UsersMePatchSerializer,
                          UsersSerializer)
from .utils import send_confirmation_email

User = get_user_model()


class UserRegistrationViewSet(mixins.CreateModelMixin,
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
                            status=status.HTTP_200_OK)


class UsersMeViewSet(GenericViewSet,
                     mixins.UpdateModelMixin,
                     mixins.RetrieveModelMixin):
    """Получение и изменение информации о текущем пользователе."""

    queryset = User.objects.all()
    serializer_class = UsersMeGetSerializer

    def get_object(self):
        return get_object_or_404(User, pk=self.request.user.pk)

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return UsersMeGetSerializer
        else:
            return UsersMePatchSerializer


class UserViewSet(viewsets.ModelViewSet):
    """Обработка прочих эндпойнтов users."""

    queryset = User.objects.all()
    serializer_class = UsersSerializer
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    pagination_class = LimitOffsetPagination
