from __future__ import annotations

from typing import Any

from users.models import User


def get_user_info(user: User, token: str | None = None) -> dict[str, Any]:
    """Get user info."""
    user_info = {
        'id': user.id,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'token': token,
        'email': user.email,
    }
    return user_info
