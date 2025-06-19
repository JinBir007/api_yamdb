from django.conf import settings
from django.core.mail import send_mail


def send_confirmation_email(user, confirmation_token, email):
    message = (f'Пожалуйста, подтвердите свой email для логина {user} на '
               f'YamDB. Ваш код подтверждения: {str(confirmation_token)}')
    send_mail(subject='Подтверждение регистрации на YamDB',
              message=message,
              from_email=settings.API_EMAIL,
              recipient_list=[email, ],
              fail_silently=True)
