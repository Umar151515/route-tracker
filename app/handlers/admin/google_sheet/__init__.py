from .get import router as get_router
from .delete import router as delete_router


routers = [
    get_router,
    delete_router
]