from django.urls.conf import path

import feeds.api.v1.views as feed_api_views


urlpatterns = [
    path('register/', feed_api_views.RegisterFeedView.as_view(), name='register'),
    path('follow/<uuid:feed_id>/', feed_api_views.FollowFeedView.as_view(), name='follow_feed'),
    path('unfollow/<uuid:feed_id>/', feed_api_views.UnFollowFeedView.as_view(), name='unfollow_feed'),
    path('mark-read/<uuid:feed_item_id>/', feed_api_views.MarkFeedItemReadView.as_view(), name='mark_read'),
    path('feed-items/<uuid:feed_id>/', feed_api_views.FeedItemListView.as_view(), name='feed_items'),
    path('filter/feed-items/', feed_api_views.FeedItemFilter.as_view(), name='filter_feed_items'),
    path('registered/', feed_api_views.RegisteredFeedsListView.as_view(), name='registered_feed'),
    path('force/update/', feed_api_views.ForceFeedUpdate.as_view(), name='force_feed_update'),
    path('fetch/notification/', feed_api_views.FeedFetchNotification.as_view(), name='fetch_notification'),
]
