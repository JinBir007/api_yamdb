from rest_framework import mixins, status
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet, ViewSet
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from .serializers import (ReviewSerializer,
                          CommentSerializer,
                          ConfirmationSerializer,
                          UserRegistrationSerializer)
from ..reviews.models import Review, Comment, EmailConfirmation
from .exceptions import WrongUsernameOrToken
from .utils import send_confirmation_email

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


# Классы для авторизации и работы с пользователями: начало

class UserRegistrationViewSet(mixins.CreateModelMixin, ViewSet, GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer

    def perform_create(self, serializer):
        username = serializer.validated_data.get('username')
        email = serializer.validated_data.get('email')
        if not User.objects.filter(username=username).exists():
            serializer.save()
        user = get_object_or_404(User, username=username)
        if EmailConfirmation.objects.filter(user=user).exists():
            confirmation = EmailConfirmation.objects.get(user=user)
            confirmation.delete()
        confirmation_object = EmailConfirmation.objects.create(
            user=user)
        confirmation_code = confirmation_object.id
        send_confirmation_email(user, confirmation_code, email)


class RegistrationConfirmation(APIView):
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
            confirmation.delete()
            refresh = RefreshToken.for_user(user)
            return Response({'token': str(refresh.access_token)},
                            status=status.HTTP_200_OK)

# Классы для авторизации и работы с пользователями: конец
