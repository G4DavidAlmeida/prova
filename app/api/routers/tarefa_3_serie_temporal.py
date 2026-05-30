from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import AppContainerDep
from app.api.dtos.tarefa_3_serie_temporal import (
    ConsultaSerieTemporalRequisicaoDTO,
    ConsultaSerieTemporalRespostaDTO,
    RegistroSerieTemporalRespostaDTO,
)

router = APIRouter(prefix="/tarefa-3", tags=["Tarefa 3 - Serie Temporal Cassandra"])


def construir_requisicao_serie_temporal(
    simbolo: str = Query(
        ...,
        description="Moeda no formato AAA-BBB. Exemplo: USD-BRL.",
    ),
    limite: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Quantidade maxima de pontos retornados da serie temporal.",
    ),
) -> ConsultaSerieTemporalRequisicaoDTO:
    return ConsultaSerieTemporalRequisicaoDTO(simbolo=simbolo.upper(), limite=limite)


@router.get(
    "/serie-temporal/ultimos",
    response_model=ConsultaSerieTemporalRespostaDTO,
    summary="Consultar serie temporal por moeda",
    description="Retorna os ultimos pontos de serie temporal armazenados no Cassandra.",
)
def consultar_serie_temporal_tarefa_3(
    container: AppContainerDep,
    requisicao: ConsultaSerieTemporalRequisicaoDTO = Depends(
        construir_requisicao_serie_temporal
    ),
) -> ConsultaSerieTemporalRespostaDTO:
    linhas = container.cassandra_repo.get_latest(
        symbol=requisicao.simbolo,
        limit=requisicao.limite,
    )
    itens = [RegistroSerieTemporalRespostaDTO.model_validate(item) for item in linhas]
    return ConsultaSerieTemporalRespostaDTO(quantidade=len(itens), itens=itens)
