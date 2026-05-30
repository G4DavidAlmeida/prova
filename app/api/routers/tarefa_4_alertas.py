from __future__ import annotations

from fastapi import APIRouter, Depends, Path

from app.api.dependencies import AppContainerDep
from app.api.dtos.tarefa_4_alertas import (
    ConsultaAlertasRequisicaoDTO,
    ConsultaAlertasRespostaDTO,
)

router = APIRouter(prefix="/tarefa-4", tags=["Tarefa 4 - Alertas Neo4j"])


def construir_requisicao_alertas(
    simbolo: str = Path(
        ...,
        description="Moeda no formato AAA-BBB. Exemplo: USD-BRL.",
    ),
) -> ConsultaAlertasRequisicaoDTO:
    return ConsultaAlertasRequisicaoDTO(simbolo=simbolo.upper())


@router.get(
    "/alertas/{simbolo}",
    response_model=ConsultaAlertasRespostaDTO,
    summary="Listar investidores para notificacao",
    description="Consulta no Neo4j os investidores que acompanham a moeda informada.",
)
def consultar_alertas_tarefa_4(
    container: AppContainerDep,
    requisicao: ConsultaAlertasRequisicaoDTO = Depends(construir_requisicao_alertas),
) -> ConsultaAlertasRespostaDTO:
    investidores = container.neo4j_repo.get_investors_for_symbol(requisicao.simbolo)
    return ConsultaAlertasRespostaDTO(
        simbolo=requisicao.simbolo,
        quantidade=len(investidores),
        investidores=investidores,
    )
