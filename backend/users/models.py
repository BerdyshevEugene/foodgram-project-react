from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


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
