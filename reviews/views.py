from rest_framework.viewsets import ModelViewSet
from serializers import ReviewSerializer, CommentSerializer, RatingSerializer
from models import Review, Comment, Rating


class ReviewViewSet(ModelViewSet):
    """ViewSet для модели Review"""""
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer


class CommentViewSet(ModelViewSet):
    """ViewSet для модели Comment"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer


class RatingViewSet(ModelViewSet):
    """ViewSet для модели Rating"""
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
