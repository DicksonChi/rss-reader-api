import uuid
from django.db import models
from django.utils.translation import ugettext_lazy as _
from utilities.models import BaseModel


class Feed(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50)
    url = models.URLField()
    registered_by = models.ForeignKey('users.User', on_delete=models.PROTECT, null=True, related_name='registered_by')
    followed_by = models.ManyToManyField('users.User', blank=True, related_name='followed_by')

    class Meta:
        """Extra model properties."""

        ordering = ['datetime_updated']


class FeedItem(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=250)
    content = models.TextField(blank=True)
    published_id = models.CharField(max_length=250, unique=True, blank=True)
    published_time = models.DateTimeField(_('Published at'), null=True, blank=True)
    author = models.CharField(max_length=250, blank=True)
    url = models.URLField(blank=True)
    feed = models.ForeignKey('feeds.Feed', on_delete=models.PROTECT)
    read_by = models.ManyToManyField('users.User', blank=True, related_name='read_by')

    class Meta:
        """Extra model properties."""

        ordering = ['datetime_updated']


class Notification(BaseModel):
    FETCH_STATUS_PENDING = 'Pending'
    FETCH_STATUS_SUCCESS = 'Success'
    FETCH_STATUS_FAILED = 'Failed'
    FETCH_STATUS_CHOICES = (
        (FETCH_STATUS_PENDING, 'Fetch Pending'),
        (FETCH_STATUS_SUCCESS, 'Fetch Success'),
        (FETCH_STATUS_FAILED, 'Fetch Failed'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    feed = models.ForeignKey('feeds.Feed', on_delete=models.PROTECT)
    fetch_status = models.CharField(max_length=50, choices=FETCH_STATUS_CHOICES, default=FETCH_STATUS_PENDING)
    number_of_retries = models.IntegerField(default=0)
