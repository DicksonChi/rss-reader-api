from __future__ import annotations

from uuid import UUID

from knox.auth import TokenAuthentication
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from feeds.api.v1.constants import FEED_ITEM_READ, FEED_ITEM_UNREAD
from feeds.api.v1.serializers import (
    RegisterFeedSerializer,
    FeedSerializer,
    FeedItemSerializer,
    FeedItemFilterSerializer,
)
from feeds.tasks import update_feed_task
from lib.feed_utils import FeedManager
from lib.user_utils import UserFeedManager
from lib.utils import AtomicMixin


# view for following - done
# view for unfollowing - done
# view for registering  feed- done
# view for listing registered feeds - done
# view for listing all feeds items - done
# view for marking items as read - done
# list for all Read feed item  and all unread feed for a user per feed or all feed - done
# view to force a feed update - done


class RegisterFeedView(AtomicMixin, APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = RegisterFeedSerializer

    def post(self, request: Request) -> Response:
        """Register a feed by a user."""
        if not request.user.is_authenticated:
            raise AssertionError('User not authenticated')
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        # create a manager object for the UserFeed and pass the validated data
        user_feed_manager = UserFeedManager(request.user)
        feed = user_feed_manager.register_feed(serializer.validated_data)
        return Response({'id': str(feed.id)}, status=status.HTTP_201_CREATED)


class FollowFeedView(AtomicMixin, APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, feed_id: UUID) -> Response:
        """User follow a feed."""
        if not request.user.is_authenticated:
            raise AssertionError('User not authenticated')
        feed_manager = FeedManager(feed_id)
        followed = feed_manager.add_follower(request.user.id)
        return (
            Response({'message': 'Successfully followed.'}, status=status.HTTP_200_OK)
            if followed
            else Response({'non_field_errors': ['Feed not found.']}, status=status.HTTP_400_BAD_REQUEST)
        )


class UnFollowFeedView(AtomicMixin, APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, feed_id: UUID) -> Response:
        """User unfollow a feed."""
        if not request.user.is_authenticated:
            raise AssertionError('User not authenticated')
        feed_manager = FeedManager(feed_id)
        removed = feed_manager.remove_follower(request.user.id)
        return (
            Response({}, status=status.HTTP_200_OK)
            if removed
            else Response({'non_field_errors': ['Feed not found.']}, status=status.HTTP_400_BAD_REQUEST)
        )


class MarkFeedItemReadView(AtomicMixin, APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request, feed_item_id: UUID) -> Response:
        """User mark a feed item as read."""
        if not request.user.is_authenticated:
            raise AssertionError('User not authenticated')
        user_feed_manager = UserFeedManager(request.user)
        marked = user_feed_manager.mark_feed_content_as_read(feed_item_id)
        return (
            Response({'message': 'Marked'}, status=status.HTTP_200_OK)
            if marked
            else Response({'non_field_errors': ['Feed item not found.']}, status=status.HTTP_400_BAD_REQUEST)
        )


class RegisteredFeedsListView(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = FeedSerializer

    def get(self, request: Request) -> Response:
        """Get feed registered to this user."""
        if not request.user.is_authenticated:  # pragma: no cover  # should not happen but mypy needs this
            raise AssertionError('User not authenticated')
        user_feed_manager = UserFeedManager(request.user)
        registered_feeds = user_feed_manager.all_registered_feed()
        serializer = self.serializer_class(instance=registered_feeds, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)


class FeedItemListView(AtomicMixin, APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = FeedItemSerializer

    def post(self, request: Request, feed_id: UUID) -> Response:
        """Get list of feed item for one feed."""
        if not request.user.is_authenticated:  # pragma: no cover  # should not happen but mypy needs this
            raise AssertionError('User not authenticated')
        feed_manager = FeedManager(feed_id)
        all_feed_items = feed_manager.get_feed_content()
        serializer = self.serializer_class(instance=all_feed_items, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class FeedItemFilter(APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    query_params_serializer = FeedItemFilterSerializer
    serializer_class = FeedItemSerializer

    def get(self, request: Request) -> Response:
        """ Build a filter for read and unread feeds."""
        if not request.user.is_authenticated:  # pragma: no cover  # should not happen but mypy needs this
            raise AssertionError('User not authenticated')
        filter_serializer = self.query_params_serializer(data=request.query_params)
        filter_serializer.is_valid(raise_exception=True)
        query_filter = {}

        # build the query filters based on the query_params
        if filter_serializer.data.get('filter_type', '') == FEED_ITEM_READ:
            # if only read articles
            query_filter['read_by__id'] = request.user.id

        if filter_serializer.data.get('feed_id'):
            # filter for a single feed
            user_feed_manager = FeedManager(filter_serializer.data['feed_id'])
            result_query = user_feed_manager.get_feed_content(query_filter)
        else:
            # filter for all feed (globally) if there is no feed_id in the params
            user_feed_manager = FeedManager()
            result_query = user_feed_manager.get_feed_content(query_filter)

        # now exclude the read items if the filter type is unread
        if filter_serializer.data.get('filter_type', '') == FEED_ITEM_UNREAD:
            # if only unread articles
            result_query = result_query.exclude(read_by__id=request.user.id)

        # order by the  datetime_updated from the most recent
        serializer = self.serializer_class(
            instance=result_query.order_by('-datetime_updated', '-feed__datetime_updated'), many=True
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class ForceFeedUpdate(AtomicMixin, APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def post(self, request: Request) -> Response:
        """User force feed update."""
        if not request.user.is_authenticated:
            raise AssertionError('User not authenticated')
        update_feed_task.delay(request.user.id)
        return Response({'message': 'Feeds are updating...'}, status=status.HTTP_200_OK)


class FeedFetchNotification(AtomicMixin, APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request: Request) -> Response:
        """User fetch feed notifications."""
        if not request.user.is_authenticated:
            raise AssertionError('User not authenticated')
        user_feed_manager = FeedManager()
        return Response(user_feed_manager.get_most_recent_feed_notification(request.user.id), status=status.HTTP_200_OK)
