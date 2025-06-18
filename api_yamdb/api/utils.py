from django.core.mail import send_mail


def send_confirmation_email(user, confirmation_code, email):
    message = (f'Пожалуйста, подтвердите свой email для логина {user} на '
               f'YamDB. Ваш код подтверждения: {str(confirmation_code)}')
    send_mail(subject='Подтверждение регистрации на YamDB',
              message=message,
              from_email='admin@yamdb.com',
              recipient_list=[email, ],
              fail_silently=True)
