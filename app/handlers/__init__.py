from .base import router as base_router
from .settings import router as settings_router
from .image_handlers import router as image_router
from .chat import router as chat_router

routers = [
    base_router,
    settings_router,
    image_router,
    chat_router
]