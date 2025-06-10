from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.utils import timezone
from .models import Review, Comment


class ReviewModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        """Тестовые данные"""
        cls.review = Review.objects.create(
            author=cls.user,
            title=cls.title,
            text=('A valid review text that exceeds'
                  ' minimum length requirement.'),
            rating=4
        )

    def test_review_creation(self):
        """Проверка корректного создания отзыва"""
        self.assertEqual(Review.objects.count(), 1)
        self.assertEqual(self.review.author, self.user)
        self.assertEqual(self.review.title, self.title)
        self.assertTrue(3 <= self.review.rating <= 5)

    def test_rating_validation(self):
        """Проверка валидации рейтинга"""
        for invalid_rating in [0, 6]:
            review = Review(
                author=self.user,
                title=self.title,
                text='Valid text',
                rating=invalid_rating
            )
            with self.assertRaises(ValidationError):
                review.full_clean()

    def test_unique_review_constraint(self):
        """Проверка уникальности отзыва от одного автора"""
        with self.assertRaises(IntegrityError):
            Review.objects.create(
                author=self.user,
                title=self.title,
                text='Another review',
                rating=5
            )

    def test_auto_timestamps(self):
        """Проверка автоматического проставления даты"""
        new_review = Review.objects.create(
            author=self.user,
            title=self.title,
            text='New review',
            rating=3
        )
        self.assertIsNotNone(new_review.pub_date)
        self.assertTrue(timezone.now() - new_review.pub_date < timezone.timedelta(seconds=1)) # noqa


class CommentModelTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        #  cls.user = User.objects.create_user(username='commenter')
        #  cls.title = Title.objects.create(name='Comment Title')
        cls.review = Review.objects.create(
            author=cls.user,
            title=cls.title,
            text='Review for comments',
            rating=4
        )

    def test_comment_creation(self):
        """Проверка создания комментария"""
        comment = Comment.objects.create(
            review=self.review,
            author=self.user,
            text='A valid comment text with proper length.'
        )
        self.assertEqual(Comment.objects.count(), 1)
        self.assertEqual(comment.review, self.review)
        self.assertIn(comment, self.review.comment_set.all())

    def test_comment_text_validation(self):
        """Проверка валидации текста комментария"""
        short_comment = Comment(
            review=self.review,
            author=self.user,
            text='Hi'
        )
        with self.assertRaises(ValidationError):
            short_comment.full_clean()

    def test_cascade_deletion(self):
        """Проверка каскадного удаления"""
        self.review.delete()
        self.assertEqual(Comment.objects.count(), 0)
        Comment.objects.create(
            review=self.review,
            author=self.user,
            text='Test comment'
        )
        self.user.delete()
        self.assertEqual(Review.objects.count(), 0)
        self.assertEqual(Comment.objects.count(), 0)
