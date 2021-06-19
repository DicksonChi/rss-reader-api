from __future__ import annotations

import uuid
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import ugettext_lazy as _


class User(AbstractUser):
    """
    Model that represents an user.

    To be active, the user must register.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)  # NOQA (ignore all errors on this line)
    first_name = models.CharField(max_length=200, blank=True)
    last_name = models.CharField(max_length=200, blank=True)
    username = models.CharField(max_length=200, default=uuid.uuid4, unique=True)
    is_staff = models.BooleanField(_('staff status'), default=False)
    is_superuser = models.BooleanField(_('superuser status'), default=False)
    is_active = models.BooleanField(_('active'), default=True)

    class Meta:
        """Extra model properties."""

        ordering = ['-date_joined']

    def __str__(self) -> str:
        """
        Unicode representation for an user model.

        :return: string
        """
        return self.email
