from __future__ import annotations

import asyncio

from fastapi import APIRouter, Body

from app.api.dependencies import AppContainerDep
from app.api.dtos.monitoramento import (
    ExecutarCicloRequisicaoDTO,
    ExecutarCicloRespostaDTO,
)

router = APIRouter(prefix="/monitoramento", tags=["Monitoramento"])


@router.post(
    "/executar-ciclo",
    response_model=ExecutarCicloRespostaDTO,
    summary="Executar ciclo manual de monitoramento",
    description="Executa um ciclo completo envolvendo cache, data lake, serie temporal e alertas.",
)
async def executar_ciclo_monitoramento(
    container: AppContainerDep,
    requisicao: ExecutarCicloRequisicaoDTO = Body(
        default_factory=ExecutarCicloRequisicaoDTO,
    ),
) -> ExecutarCicloRespostaDTO:
    resumo = await asyncio.to_thread(
        container.ingestion_service.run_cycle,
        requisicao.forcar_consulta_api,
    )

    return ExecutarCicloRespostaDTO(
        data_hora_ciclo=resumo["timestamp"],
        cache=resumo["cache"],
        escritas_mongo=resumo["mongo_writes"],
        escritas_cassandra=resumo["cassandra_writes"],
        alertas=resumo["alerts"],
    )
