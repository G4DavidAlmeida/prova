from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from app.api.dependencies import AppContainerDep
from app.api.dtos.tarefa_2_datalake import (
    ConsultaDatalakeRequisicaoDTO,
    ConsultaDatalakeRespostaDTO,
    RegistroDatalakeRespostaDTO,
)

router = APIRouter(prefix="/tarefa-2", tags=["Tarefa 2 - Data Lake MongoDB"])


def construir_requisicao_datalake(
    simbolo: str | None = Query(
        default=None,
        description="Filtro opcional de moeda no formato AAA-BBB.",
    ),
    limite: int = Query(
        default=10,
        ge=1,
        le=100,
        description="Quantidade maxima de registros retornados.",
    ),
) -> ConsultaDatalakeRequisicaoDTO:
    simbolo_normalizado = simbolo.upper() if simbolo else None
    return ConsultaDatalakeRequisicaoDTO(simbolo=simbolo_normalizado, limite=limite)


def _converter_registro_datalake(documento: dict[str, Any]) -> RegistroDatalakeRespostaDTO:
    return RegistroDatalakeRespostaDTO(
        id_documento=str(documento.get("_id", "")),
        moeda=str(documento.get("Moeda", "")),
        valor=str(documento.get("Valor", "")),
        variacao=str(documento.get("Variacao", "")),
        data_coleta=str(documento.get("data_coleta", "")),
        fonte=str(documento.get("fonte", "")),
        origem_preco=str(documento.get("origem_preco", "")),
        payload_api=documento.get("payload_api", {}),
        data_api=documento.get("data_api"),
    )


@router.get(
    "/datalake/ultimos",
    response_model=ConsultaDatalakeRespostaDTO,
    summary="Consultar ultimos registros do Data Lake",
    description="Retorna os documentos mais recentes armazenados no MongoDB.",
)
def consultar_datalake_tarefa_2(
    container: AppContainerDep,
    requisicao: ConsultaDatalakeRequisicaoDTO = Depends(construir_requisicao_datalake),
) -> ConsultaDatalakeRespostaDTO:
    documentos = container.mongo_repo.get_latest(
        symbol=requisicao.simbolo,
        limit=requisicao.limite,
    )
    itens = [_converter_registro_datalake(documento) for documento in documentos]
    return ConsultaDatalakeRespostaDTO(quantidade=len(itens), itens=itens)
