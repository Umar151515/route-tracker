from .base import router as base_router
from .settings import router as settings_router
from .passengers import router as passengers_router
from .admin.user import routers as admin_user_routers
from .admin.bus import routers as admin_bus_routers
from .admin.google_sheet import routers as admin_google_sheet_routers
from .admin.log import router as log_touter


routers = [
    base_router,
    settings_router,
    passengers_router,
    log_touter,
    *admin_bus_routers,
    *admin_google_sheet_routers,
    *admin_user_routers
]