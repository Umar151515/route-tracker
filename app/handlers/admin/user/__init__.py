from .get import router as get_user_router
from .edit import router as edit_user_router
from .add import router as add_user_router
from .delete import router as delete_user_router
from .auto_lookup import router as auto_lookup_user_router


routers = [
    get_user_router,
    edit_user_router,
    add_user_router,
    delete_user_router,
    auto_lookup_user_router
]