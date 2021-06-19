from unittest import mock
from django.urls import reverse
from feedparser.util import FeedParserDict
from django.test.utils import override_settings
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from feeds.tasks import update_feed_task
from users.models import User
from feeds.models import Feed, FeedItem, Notification


def mock_feed_parser_result(feed):
    new_feed_parser = FeedParserDict(bozo=False, entries=[], feed=FeedParserDict(), headers={},)
    entries = []
    for i in range(0, 10):
        entry_feed_parser = FeedParserDict()
        entry_feed_parser['title'] = 'Test Title'
        entry_feed_parser['summary'] = 'Test summary'
        entry_feed_parser['link'] = 'http://testlink.com/{}/'.format(str(i))
        entry_feed_parser['id'] = 'http://testlink.com/{}/'.format(str(i))
        entry_feed_parser['author'] = 'dickson chibuzor'
        entry_feed_parser['published'] = str(timezone.now())

        entries.append(entry_feed_parser)
    new_feed_parser['entries'] = entries

    return new_feed_parser


class TestUserRegisterFeed(APITestCase):
    def setUp(self) -> None:
        data = {'first_name': 'Dickson', 'last_name': 'Chibuzor', 'email': 'dickson@test.com', 'password': 'password'}

        url = reverse('users_api_v1:register')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.new_user = User.objects.get(id=response.json().get('id'))
        self.token = response.json().get('token', '')

    def test_register_and_retrieve_feed(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'faketoken')
        url = reverse('feeds_api_v1:register')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        data = {'name': 'Algemeen', 'url': 'http://www.nu.nl/rss/Algemeen'}
        url = reverse('feeds_api_v1:register')
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        # get registered feed
        url = reverse('feeds_api_v1:registered_feed')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list(response.json())), 1)


class TestFeedActionView(APITestCase):
    def setUp(self) -> None:
        data = {'first_name': 'Dickson', 'last_name': 'Chibuzor', 'email': 'dickson@test.com', 'password': 'password'}

        url = reverse('users_api_v1:register')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.new_user = User.objects.get(id=response.json().get('id'))
        self.token = response.json().get('token', '')

        self.feed = Feed.objects.create(
            name='Algemeen', url='http://www.nu.nl/rss/Algemeen', registered_by=self.new_user
        )

    def test_follow_unfollow_feed(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'faketoken')
        url = reverse('feeds_api_v1:follow_feed', kwargs={'feed_id': self.feed.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(self.feed.followed_by.filter(id=self.new_user.id).exists())

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.feed.refresh_from_db()
        self.assertTrue(self.feed.followed_by.filter(id=self.new_user.id).exists())

        # test for unfollow feed
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'faketoken')
        url = reverse('feeds_api_v1:unfollow_feed', kwargs={'feed_id': self.feed.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.feed.refresh_from_db()
        self.assertFalse(self.feed.followed_by.filter(id=self.new_user.id).exists())


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class TestFeedItemActionReadView(APITestCase):
    def setUp(self) -> None:
        data = {'first_name': 'Dickson', 'last_name': 'Chibuzor', 'email': 'dickson@test.com', 'password': 'password'}

        url = reverse('users_api_v1:register')
        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.new_user = User.objects.get(id=response.json().get('id'))
        self.token = response.json().get('token', '')

        self.feed = Feed.objects.create(
            name='Algemeen', url='http://www.nu.nl/rss/Algemeen', registered_by=self.new_user
        )
        self.feed.followed_by.add(self.new_user)

        self.feedItem1 = FeedItem.objects.create(
            title='Test Title',
            content='Test Content',
            published_id='published id 1',
            published_time=timezone.now(),
            author='Author A',
            url='http://www.nu.nl/rss/Algemeen/1',
            feed=self.feed,
        )
        self.feedItem2 = FeedItem.objects.create(
            title='Test Title',
            content='Test Content',
            published_id='published id 2',
            published_time=timezone.now(),
            author='Author A',
            url='http://www.nu.nl/rss/Algemeen/2',
            feed=self.feed,
        )

    def test_mark_item_as_read(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'faketoken')
        url = reverse('feeds_api_v1:mark_read', kwargs={'feed_item_id': self.feedItem1.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(self.feedItem1.read_by.filter(id=self.new_user.id).exists())

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.feed.refresh_from_db()
        self.assertTrue(self.feedItem1.read_by.filter(id=self.new_user.id).exists())

    def test_feed_items(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'faketoken')
        url = reverse('feeds_api_v1:feed_items', kwargs={'feed_id': self.feed.id})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list(response.json())), 2)

    def test_filter_feed_items(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'faketoken')
        url = reverse('feeds_api_v1:filter_feed_items')
        response = self.client.get(url, {'feed_id': self.feed.id, 'filter_type': 'read'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get(url, {'feed_id': self.feed.id, 'filter_type': 'read'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list(response.json())), 0)
        response = self.client.get(url, {'feed_id': self.feed.id, 'filter_type': 'unread'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list(response.json())), 2)

        self.feedItem1.read_by.add(self.new_user)
        response = self.client.get(url, {'feed_id': self.feed.id, 'filter_type': 'unread'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list(response.json())), 1)

        self.feedItem1.read_by.add(self.new_user)
        response = self.client.get(url, {'filter_type': 'unread'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(list(response.json())), 1)

    def test_force_feed_update(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'faketoken')
        url = reverse('feeds_api_v1:force_feed_update')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        url = reverse('feeds_api_v1:force_feed_update')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json().get('message'), 'Feeds are updating...')

    @mock.patch('feeds.tasks.feed_parser', mock_feed_parser_result)
    def test_feed_fetch_notification(self):
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + 'faketoken')
        url = reverse('feeds_api_v1:fetch_notification')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 0)

        previous_count = FeedItem.objects.count()
        update_feed_task()
        self.assertEqual(Notification.objects.count(), 1)
        self.assertEqual(FeedItem.objects.count(), (previous_count + 10))

        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
