from __future__ import annotations

from uuid import UUID
from django.db.models.query import QuerySet

from typing import Any

from feeds.models import Feed, FeedItem
from users.models import User


class UserFeedManager:
    def __init__(self, user: User) -> None:
        """Initialize the UserFeedManager class."""
        self.user = user

    def register_feed(self, feed_data: dict[str, Any]) -> Feed:
        """Register a new feed."""
        feed_data['registered_by'] = self.user
        return Feed.objects.create(**feed_data)

    def mark_feed_content_as_read(self, feed_item_id: UUID) -> bool:
        """Mark a feed as read."""
        try:
            feed_item = FeedItem.objects.get(id=feed_item_id)
        except FeedItem.DoesNotExist:
            return False
        feed_item.read_by.add(self.user)

        return True

    def all_registered_feed(self) -> 'QuerySet[Feed]':
        """All the registered feed by the user"""
        return Feed.objects.filter(registered_by=self.user)
