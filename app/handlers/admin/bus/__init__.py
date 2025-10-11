from .bus_info import router as bus_info_router
from .bus_add import router as bus_add_router
from .bus_remove import router as bus_remove_router
from .stop_add import router as stop_add_router
from .stop_remove import router as stop_remove_router


routers = [
    bus_info_router,
    bus_add_router,
    bus_remove_router,
    stop_add_router,
    stop_remove_router
]