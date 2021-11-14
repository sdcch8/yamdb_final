from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from users.validators import username_not_me_validator


class User(AbstractUser):
    USER = 'user'
    MODERATOR = 'moderator'
    ADMIN = 'admin'

    CHOICES = [(USER, 'user'),
               (MODERATOR, 'moderator'),
               (ADMIN, 'admin')]

    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        'Username',
        max_length=150,
        unique=True,
        help_text=('Required. 150 characters or fewer.'
                   'Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator, username_not_me_validator],
        error_messages={
            'unique': ('A user with that username already exists.'),
        },
    )
    first_name = models.CharField(
        'first name',
        max_length=30,
        blank=True,
        null=True,
    )
    last_name = models.CharField(
        'last name',
        max_length=150,
        blank=True,
        null=True,
    )
    email = models.EmailField(
        'Email address',
        blank=False,
        null=False,
        max_length=254,
        unique=True,
        error_messages={
            'unique': ('A user with that email already exists.'),
        })
    bio = models.TextField(
        'Biography',
        blank=True,
        null=True,
    )
    role = models.CharField(
        'User role',
        max_length=9,
        choices=CHOICES,
        blank=False,
        default=USER,
        null=False,
    )

    class Meta:
        ordering = ['-id']
