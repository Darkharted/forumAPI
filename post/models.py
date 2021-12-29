from django.db import models
from django.db.models.base import Model
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.contrib.contenttypes.fields import GenericRelation
from forum import settings
from likes.models import Like
from django.dispatch import receiver
from django.db.models.signals import post_save, pre_save
from .tasks import notify_user_func


class Created(models.Model):
    """
    Нужен для того чтобы, во всех моделях не прописовали одно и тоже поле
    все последующие модели будут наследоваться от этого класса и буду принимать его поля
    """
    created = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        """
        Значение abstract = True означает что при
        создание файлов миграциия для нашей модели
        эти файлы не будут создавться
        """
        abstract = True


class Post(Created):
    title = models.CharField(max_length=50)
    description = models.TextField()
    author = models.ForeignKey(
        'account.CustomUser', on_delete=models.CASCADE,
        related_name='problems'
    )
    moderated = models.BooleanField(default=False)
    likes = GenericRelation(Like)

    @property
    def total_likes(self):
        return self.likes.count()

    def __str__(self):
        return self.title


class Picture(Created):
    image = models.ImageField(
        upload_to='pictures'
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='pictures'
    )


class Comment(Created):
    text = models.TextField()
    author = models.ForeignKey(
        'account.CustomUser', on_delete=models.CASCADE,
        related_name='comments'
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='comments'
    )

    def __str__(self):
        return self.text

    @receiver(post_save, sender=Post)
    def notify_user_func(sender, instance, created, **kwargs):
        if created:
            email = instance.author.email
            notify_user_func.delay(email)


class Rating(Created):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='rating'
    )
    author = models.ForeignKey(
        'account.CustomUser', on_delete=models.CASCADE,
        related_name='rating', null=True
    )
    rating = models.PositiveIntegerField()


class Favorite(models.Model):
    user = models.ForeignKey('account.CustomUser', on_delete=models.CASCADE, related_name='favorites')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='favorites')
    favorite = models.BooleanField(default=True)





