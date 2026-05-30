from .geral import router as geral_router
from .monitoramento import router as monitoramento_router
from .tarefa_1_cache import router as tarefa_1_cache_router
from .tarefa_2_datalake import router as tarefa_2_datalake_router
from .tarefa_3_serie_temporal import router as tarefa_3_serie_temporal_router
from .tarefa_4_alertas import router as tarefa_4_alertas_router

__all__ = [
    "geral_router",
    "monitoramento_router",
    "tarefa_1_cache_router",
    "tarefa_2_datalake_router",
    "tarefa_3_serie_temporal_router",
    "tarefa_4_alertas_router",
]