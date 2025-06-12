from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model

from .serializers import ReviewSerializer, CommentSerializer
from ..reviews.models import Review, Comment

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
