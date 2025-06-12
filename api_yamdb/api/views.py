from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import (
    ModelViewSet,
    ReadOnlyModelViewSet,
)

from ..content.models import Category, Genre, Title
from ..reviews.models import Comment, Review
from .serializers import (
    CategorySerializer,
    CommentSerializer,
    GenreSerializer,
    ReviewSerializer,
    TitleSerializer,
)


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
