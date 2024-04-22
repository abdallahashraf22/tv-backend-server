from apps.genres import genres_router
from apps.users import users_router
from apps.content import content_router
from apps.users_actions import actions_router
from apps.device_management import device_router


__all__ = ["content_router", "genres_router", "users_router", "actions_router", "device_router"]
