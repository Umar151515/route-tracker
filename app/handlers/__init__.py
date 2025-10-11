from .base import router as base_router
from .settings import router as settings_router
from .passengers import router as passengers_router
from .admin.user import routers as admin_user_routers
from .admin.bus import routers as admin_bus_routers


routers = [
    base_router,
    settings_router,
    passengers_router,
    *admin_bus_routers,
    *admin_user_routers
]