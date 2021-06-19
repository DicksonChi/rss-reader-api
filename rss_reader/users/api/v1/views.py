from __future__ import annotations
from django.contrib.auth.models import update_last_login
from django.utils import timezone
from knox.auth import TokenAuthentication
from knox.models import AuthToken
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from users.api.v1.serializers import UserLoginSerializer, UserRegisterSerializer
from users.api.v1.utils import get_user_info
from lib.utils import AtomicMixin


class UserRegisterView(AtomicMixin, APIView):
    serializer_class = UserRegisterSerializer

    def post(self, request: Request) -> Response:
        """User register."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        user.set_password(serializer.validated_data['password'])
        user.save()

        update_last_login(None, user)  # type: ignore
        # create token
        _, token = AuthToken.objects.create(user)
        user_data = get_user_info(user, token)

        return Response(user_data, status=status.HTTP_200_OK)


class UserLoginView(AtomicMixin, APIView):
    authentication_classes = ()
    permission_classes = ()
    serializer_class = UserLoginSerializer

    def post(self, request: Request) -> Response:
        """User login."""
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['email']
        user.last_login = timezone.localtime()
        user.save(update_fields=['last_login'])

        # create token
        _, token = AuthToken.objects.create(user)

        user_data = get_user_info(user, token)

        return Response(user_data, status=status.HTTP_200_OK)


class UserLogoutView(AtomicMixin, APIView):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)
    serializer_class = None

    def post(self, request: Request) -> Response:
        """User logout."""
        request._auth.delete()  # noqa
        return Response({}, status=status.HTTP_204_NO_CONTENT)
