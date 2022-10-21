from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)
    USER = 'user'
    ADMIN = 'admin'

    ROLES = (
        (USER, 'Пользователь'),
        (ADMIN, 'Администратор'),
    )

    username = models.TextField('Пользователь',
                                unique=True,
                                max_length=150
                                )
    role = models.CharField('Роль',
                            max_length=10,
                            choices=ROLES,
                            default=USER)
    first_name = models.TextField('Имя',
                                  max_length=150)
    last_name = models.TextField('Фамилия',
                                 max_length=150)
    email = models.EmailField('E-mail',
                              unique=True,
                              max_length=254)

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_superuser

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        if self.username:
            return self.username
        return self.email


class Subscribe(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text='выберите пользователя',
        related_name='follower',
        verbose_name='подписчик',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        help_text='выберите, на кого подписаться',
        related_name='subscribing',
        verbose_name='автор',
    )
    subscription_date = models.DateField(
        auto_now_add=True,
        verbose_name='дата подписки'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        ordering = ['id']
        constraints = [models.UniqueConstraint(
            fields=['user', 'author'],
            name='unique_subscription')
        ]
