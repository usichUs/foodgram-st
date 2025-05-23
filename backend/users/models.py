from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(
        unique=True,
        max_length=254,
        verbose_name=_('Электронная почта'),
        help_text=_('Укажите уникальный email')
    )
    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w.@+-]+\Z',
            message=_('Недопустимое имя пользователя')
        )],
        verbose_name=_('Никнейм'),
        help_text=_('Введите уникальный ник')
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name=_('Имя'),
        help_text=_('Укажите имя')
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name=_('Фамилия'),
        help_text=_('Укажите фамилию')
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name=_('Аватар'),
        help_text=_('Загрузите изображение профиля')
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        ordering = ['username']
        verbose_name = _('Пользователь')
        verbose_name_plural = _('Пользователи')

    def __str__(self):
        return self.email
