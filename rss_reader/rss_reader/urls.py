"""rss_reader URL Configuration"""
from django.conf.urls import include
from django.contrib import admin
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path('admin/', admin.site.urls),
    # API base end points
    path('api/v1/users/', include(('users.api.v1.urls', 'users_api_v1'), namespace='users_api_v1')),
    path('api/v1/feeds/', include(('feeds.api.v1.urls', 'users_api_v1'), namespace='feeds_api_v1')),
    # API Documentation
    path('api/v1/openapi/schema/', SpectacularAPIView.as_view(), name='openapi_schema'),
    path(
        'api/v1/docs/',
        SpectacularSwaggerView.as_view(template_name='documentation-ui.html', url_name='openapi_schema'),
        name='api_docs',
    ),
]
