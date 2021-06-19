from django.db import models
from django.utils.translation import ugettext_lazy as _  # NOQA


class BaseModel(models.Model):
    """More lean base model."""

    datetime_updated = models.DateTimeField(_('Last update at'), auto_now=True)
    datetime_created = models.DateTimeField(_('Created at'), auto_now_add=True)

    objects = models.Manager()

    class Meta:
        """Class meta."""

        abstract = True
