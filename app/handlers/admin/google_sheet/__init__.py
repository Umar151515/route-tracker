from .get_data import router as data_router
from .get_stats import router as statistics_router
from .delete import router as delete_router


routers = [
    data_router,
    statistics_router,
    delete_router
]