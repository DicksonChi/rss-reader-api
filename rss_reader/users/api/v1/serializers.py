from __future__ import annotations
from typing import Any, Dict
from rest_framework.fields import CharField, EmailField
from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework.exceptions import ValidationError

from users.models import User


class UserRegisterSerializer(ModelSerializer[User]):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'password']
        extra_kwargs = {
            'first_name': {'required': True, 'allow_blank': False},
            'last_name': {'required': True, 'allow_blank': False},
            'email': {'required': True},
            'password': {'required': True},
        }

    def validate_email(self, value: str) -> str:
        """Check if user exists with this email."""
        email = value.strip().lower()
        if User.objects.filter(email__iexact=email, is_active=True).exists():
            raise ValidationError('User with this email already exists.')
        return email


class UserLoginSerializer(Serializer[Dict[str, Any]]):  # pylint: disable=abstract-method
    email = EmailField()
    password = CharField()

    def validate_email(self, value: str) -> User:
        """Validate if email exists."""
        email = value.strip().lower()
        try:
            user = User.objects.get(email__iexact=email, is_active=True)
        except User.DoesNotExist:
            raise ValidationError('Please enter a correct email and password.')
        return user

    def validate(self, attrs: dict[str, Any]) -> dict[str, Any]:
        """Validate if user authenticates successfully."""
        user = attrs.get('email')
        password = attrs.get('password')
        if not user.check_password(password):  # type: ignore
            raise ValidationError({'email': ['Please enter a correct email and password.']})
        return attrs
