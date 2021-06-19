from __future__ import annotations
from typing import Any
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from drf_spectacular.extensions import OpenApiAuthenticationExtension


class KnoxTokenScheme(OpenApiAuthenticationExtension):
    target_class = 'knox.auth.TokenAuthentication'
    name = 'Token Authorization'

    def get_security_definition(self, auto_schema):
        """This adds the token API used in this project for authorization as an option for openApiAuthentication."""
        return {
            'type': 'apiKey',
            'in': 'header',
            'name': 'Authorization',
            'description': _(
                'Token-based authentication with required prefix "Token".\n \n'
                ' After user registration or login a token is returned which will be used in the token.'
            ),
        }


class AtomicMixin:
    """
    Ensure we rollback db transactions on exceptions.

    """

    @transaction.atomic()
    def dispatch(self, request: Any, *args: Any, **kwargs: Any) -> Any:
        """Atomic transaction."""
        return super(AtomicMixin, self).dispatch(request, *args, **kwargs)  # type: ignore

    def handle_exception(self, *args: Any, **kwargs: Any) -> Any:
        """Handle exception with transaction rollback."""
        response = super(AtomicMixin, self).handle_exception(*args, **kwargs)  # type: ignore

        if getattr(response, 'exception'):
            # We've suppressed the exception but still need to rollback any transaction.
            transaction.set_rollback(True)

        return response
