from __future__ import annotations

from typing import Any, Dict, OrderedDict

from rest_framework.exceptions import ValidationError
from rest_framework.fields import ChoiceField, UUIDField
from rest_framework.serializers import ModelSerializer, Serializer

from feeds.api.v1.constants import FEED_ITEM_READ, FEED_ITEM_UNREAD
from feeds.models import Feed, FeedItem


class RegisterFeedSerializer(ModelSerializer[Feed]):
    class Meta:
        model = Feed
        fields = ['name', 'url']

        extra_kwargs = {'name': {'required': True}, 'url': {'required': True, 'allow_blank': False}}

    def validate_url(self, value: str) -> str:
        """Check if url already exists to avoid multiple registering."""
        url = value.strip().lower()
        if Feed.objects.filter(url__iexact=url).exists():
            raise ValidationError('User with this email already exists.')
        return url


class FeedSerializer(ModelSerializer[Feed]):
    class Meta:
        model = Feed
        fields = ['id', 'name', 'url', 'datetime_created', 'datetime_updated']

    def to_representation(self, instance: Feed) -> dict[str, Any]:
        """Representation of this data."""
        data = {
            'id': instance.id,
            'name': instance.name,
            'url': instance.url,
            'datetime_created': str(instance.datetime_created),
            'datetime_updated': str(instance.datetime_updated),
        }
        return data


class FeedItemSerializer(ModelSerializer[FeedItem]):
    class Meta:
        model = FeedItem
        fields = ['id', 'title', 'content', 'url', 'author', 'published_time', 'datetime_created', 'datetime_updated']

    def to_representation(self, instance: FeedItem) -> dict[str, Any]:
        """Representation of this data."""
        data = {
            'id': instance.id,
            'title': instance.title,
            'content': instance.content,
            'url': instance.url,
            'author': instance.author,
            'published_time': str(instance.published_time),
            'datetime_created': str(instance.datetime_created),
            'datetime_updated': str(instance.datetime_updated),
        }
        return data


class FeedItemFilterSerializer(Serializer[Dict[str, Any]]):
    filter_type = ChoiceField(choices=[FEED_ITEM_READ, FEED_ITEM_UNREAD])  # make this a required field
    feed_id = UUIDField(required=False, allow_null=True)  # optional field. if not added then we assume it is global
