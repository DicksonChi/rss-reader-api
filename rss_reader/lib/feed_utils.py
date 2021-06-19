from __future__ import annotations

from typing import Any
from uuid import UUID
from django.db.models.query import QuerySet
from users.models import User
from feeds.models import Feed, FeedItem, Notification


class FeedManager:
    def __init__(self, feed_id: UUID | None = None) -> None:
        """Initialize the FeedManager class."""
        self.feed: Feed | None = None
        if feed_id:
            try:
                self.feed = Feed.objects.get(id=feed_id)
            except Feed.DoesNotExist:
                self.feed = None

    def add_follower(self, user_id: UUID) -> bool:
        """Add a user as a follower to a feed."""
        if self.feed:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return False
            self.feed.followed_by.add(user)
            return True
        return False

    def remove_follower(self, user_id: UUID) -> bool:
        """Remove a user as a follower to a feed."""
        if self.feed:
            try:
                user = User.objects.get(id=user_id)
            except User.DoesNotExist:
                return False
            self.feed.followed_by.remove(user)
            return True
        return False

    def get_feed_content(self, query_filter: dict[str, Any] | None = None) -> 'QuerySet[FeedItem]':
        """Get all the feed content for all feeds or just this feed."""
        if self.feed:
            return (
                FeedItem.objects.filter(feed=self.feed, **query_filter)
                if query_filter
                else FeedItem.objects.filter(feed=self.feed)
            )
        return FeedItem.objects.filter(**query_filter) if query_filter else FeedItem.objects.all()

    def get_most_recent_feed_notification(self, user_id: UUID) -> list[dict[str, Any]]:
        """Get the most recent feed notification of all the feed the user follow."""
        all_feed = Feed.objects.filter(followed_by__id=user_id)
        result = []
        for feed in all_feed:
            try:
                last_notification = Notification.objects.filter(feed=feed).latest('datetime_created')
            except Notification.DoesNotExist:
                continue
            result.append(
                {
                    'feed_id': str(feed.id),
                    'last_fetch_status': last_notification.fetch_status,
                    'time_of_notification': str(last_notification.datetime_created),
                }
            )
        return result
