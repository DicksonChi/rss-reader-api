from __future__ import annotations

from uuid import UUID
from celery import Task
from feedparser import parse as feed_parser
from feedparser.exceptions import ThingsNobodyCaresAboutButMe
from dateutil.parser import parse
from django.conf import settings
from django.utils import timezone

from feeds.models import Feed, FeedItem, Notification
from rss_reader.celery import app


def _fetch_and_update_feed(feed: Feed) -> bool:
    """Fetch feed content and update."""
    parsed_feed = feed_parser(feed.url)

    if parsed_feed:
        for entry in parsed_feed.entries:
            if not FeedItem.objects.filter(published_id=entry.id).exists():
                # so we don't need to duplicate the entries
                FeedItem.objects.create(
                    title=entry.title,
                    content=entry.summary,
                    url=entry.link,
                    published_id=entry.id,
                    author=entry.author,
                    published_time=parse(entry.published),
                    feed=feed,
                )
        feed.datetime_updated = timezone.now()
        feed.save(update_fields=['datetime_updated'])
    return True


@app.task(
    name='update_feed_task', bind=True, max_retries=settings.MAX_RETRIES, default_retry_delay=settings.RETRY_DELAY,
)  # max_retries and default_retry_delay are parameters for backoff mechanism
def update_feed_task(self: Task, user_id: UUID | None = None) -> bool:
    """Task to update feeds for a particular user."""
    if user_id:
        all_feed = Feed.objects.filter(followed_by__id=user_id)
    else:
        all_feed = Feed.objects.all()
    for feed in all_feed:
        new_notification, _ = Notification.objects.get_or_create(
            feed=feed, fetch_status=Notification.FETCH_STATUS_PENDING
        )
        try:
            _fetch_and_update_feed(feed)
            # if it  succeeds then we can set the notification as success
            new_notification.fetch_status = Notification.FETCH_STATUS_SUCCESS
            new_notification.save()
        except ThingsNobodyCaresAboutButMe as ex:
            if self.request.retries == self.max_retries:
                # if we get to the end of the retries then we should set the notification to failed.
                # Normally you send an email to notify user or maybe send it to a webhook if you are sending
                # it to another service but for this project we will have an endpoint they can check notifications
                new_notification.fetch_status = Notification.FETCH_STATUS_FAILED
            new_notification.number_of_retries = self.request.retries
            new_notification.save()

            # Retry
            self.retry(exc=ex)

    return True
