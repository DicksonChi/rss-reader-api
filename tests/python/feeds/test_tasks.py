from unittest import mock
from django.conf import settings

from feedparser.exceptions import ThingsNobodyCaresAboutButMe
from django.test import override_settings, TestCase

from feeds.models import Feed, Notification
from feeds.tasks import update_feed_task
from tests.python.feeds.apis.test_views import mock_feed_parser_result
from users.models import User


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestTasks(TestCase):
    def setUp(self) -> None:
        user_info = {
            'first_name': 'Dickson',
            'last_name': 'Chibuzor',
            'email': 'dickson@test.com',
            'password': 'password',
        }
        self.new_user = User.objects.create(**user_info)

        self.feed = Feed.objects.create(
            name='Algemeen', url='http://www.nu.nl/rss/Algemeen', registered_by=self.new_user
        )
        self.feed.followed_by.add(self.new_user)

    @mock.patch('feeds.tasks._fetch_and_update_feed')
    def test_fetch_feeds_update_failed(self, feed_parser):
        feed_parser.side_effect = ThingsNobodyCaresAboutButMe()
        update_feed_task.delay()
        notifications = Notification.objects.filter(feed=self.feed)
        self.assertTrue(notifications.exists())
        self.assertEqual(notifications.first().fetch_status, Notification.FETCH_STATUS_FAILED)
        # number of times retried before it failed
        self.assertEqual(notifications.first().number_of_retries, settings.MAX_RETRIES)

    @mock.patch('feeds.tasks.feed_parser', mock_feed_parser_result)
    def test_fetch_feeds_update_success(self):
        update_feed_task.delay()
        notifications = Notification.objects.filter(feed=self.feed)
        self.assertTrue(notifications.exists())
        self.assertEqual(notifications.first().fetch_status, Notification.FETCH_STATUS_SUCCESS)
        # number of times retried before it passed
        self.assertEqual(notifications.first().number_of_retries, 0)

    @mock.patch('feeds.tasks.feed_parser')
    def test_fetch_feeds_update_failed_then_succeed(self, feed_parser):
        feed_parser.side_effect = [ThingsNobodyCaresAboutButMe(), ThingsNobodyCaresAboutButMe(), None]
        feed_parser.return_value = mock_feed_parser_result
        # start the task for the update
        update_feed_task.delay()
        notifications = Notification.objects.filter(feed=self.feed)
        # check if the notification exists
        self.assertTrue(notifications.exists())
        self.assertEqual(notifications.first().fetch_status, Notification.FETCH_STATUS_SUCCESS)
        # number of times retried before it passed
        # this is dependent on how many times it hits the exception before it doesn't
        self.assertEqual(notifications.first().number_of_retries, 1)
