from __future__ import annotations

from fastapi import APIRouter

from .routers import (
    geral_router,
    monitoramento_router,
    tarefa_1_cache_router,
    tarefa_2_datalake_router,
    tarefa_3_serie_temporal_router,
    tarefa_4_alertas_router,
)


router = APIRouter()
router.include_router(geral_router)
router.include_router(monitoramento_router)
router.include_router(tarefa_1_cache_router)
router.include_router(tarefa_2_datalake_router)
router.include_router(tarefa_3_serie_temporal_router)
router.include_router(tarefa_4_alertas_router)
