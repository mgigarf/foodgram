from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from .constants import (MAX_EMAIL_LENGTH, NAME_LENGTH, PASSWORD_LENGTH,
                        USERNAME_REGEX)
from .validators import not_allowed_user_name


class User(AbstractUser):
    """Модель пользователя."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = (
        'username',
        'first_name',
        'last_name',
        'password'
    )

    username = models.CharField(
        verbose_name='Ник',
        max_length=NAME_LENGTH,
        unique=True,
        validators=(RegexValidator(USERNAME_REGEX), not_allowed_user_name),
    )
    email = models.EmailField(
        verbose_name='Эл. Почта',
        max_length=MAX_EMAIL_LENGTH,
        unique=True,
    )
    password = models.CharField(
        max_length=PASSWORD_LENGTH,
        verbose_name='Пароль',
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=NAME_LENGTH,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=NAME_LENGTH,
    )
    avatar = models.ImageField(
        verbose_name='Аватарка',
        upload_to='users/avatars/',
        null=True,
        default=None
    )

    class Meta:
        ordering = ('date_joined',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписок."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='follower'

    )
    following = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='На кого подписан',
        related_name='following'

    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='unique_following_pair'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('following')),
                name='self_sub_prohibited'
            )

        ]
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        default_related_name = 'following'

    def __str__(self):
        return f'Подписки {self.user} на {self.following}'
