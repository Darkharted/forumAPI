from django.core.mail import send_mail
from forum._celery import app


@app.task
def notify_user_func(email):
    send_mail(
        'Вы создали новый запрос!',
        'Спасиобо за использование нашего сайта',
        'test@gmail.com',
        [email, ]
    )
