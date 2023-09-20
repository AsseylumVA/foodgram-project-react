from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ADMIN = 'admin'
    MODER = 'moderator'
    USER = 'user'
    ROLE_CHOICES = (
        (ADMIN, 'admin'),
        (MODER, 'moderator'),
        (USER, 'user'),
    )

    email = models.EmailField(
        'Электронная почта',
        unique=True,
    )

    bio = models.TextField(
        'Биография',
        blank=True,
    )
    role = models.CharField(
        'Роль',
        max_length=25,
        choices=ROLE_CHOICES,
        default=USER
    )
    confirmation_code = models.TextField(
        'Код подтверждения',
        blank=True
    )

    @property
    def is_admin(self):
        return self.role == self.ADMIN or self.is_staff

    @property
    def is_moderator(self):
        return self.role == self.MODER or self.is_admin
