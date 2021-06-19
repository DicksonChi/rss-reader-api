from django.urls.conf import path

import users.api.v1.views as users_api_views


urlpatterns = [
    path('register/', users_api_views.UserRegisterView.as_view(), name='register'),
    path('login/', users_api_views.UserLoginView.as_view(), name='login'),
    path('logout/', users_api_views.UserLogoutView.as_view(), name='logout'),
]
