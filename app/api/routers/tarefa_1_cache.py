from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Path

from app.api.dependencies import AppContainerDep
from app.api.dtos.tarefa_1_cache import (
    ConsultaCacheRequisicaoDTO,
    CotacaoCacheRespostaDTO,
)
from app.services.market_provider import MarketProviderError

router = APIRouter(prefix="/tarefa-1", tags=["Tarefa 1 - Cache Redis"])


def construir_requisicao_cache(
    simbolo: str = Path(
        ...,
        description="Simbolo da moeda no formato AAA-BBB. Exemplo: USD-BRL.",
    ),
) -> ConsultaCacheRequisicaoDTO:
    return ConsultaCacheRequisicaoDTO(simbolo=simbolo.upper())


@router.get(
    "/cache/{simbolo}",
    summary="Consultar cotacao em cache",
    description=(
        "Consulta a cotacao no Redis. Em caso de cache miss, busca na API de mercado, "
        "atualiza o Redis com TTL e retorna o valor encontrado."
    ),
)
def consultar_cache_tarefa_1(
    container: AppContainerDep,
    requisicao: ConsultaCacheRequisicaoDTO = Depends(construir_requisicao_cache),
) -> CotacaoCacheRespostaDTO:
    payload = container.redis_repo.get_quote(requisicao.simbolo)
    if payload is None:
        if requisicao.simbolo not in container.settings.symbols:
            raise HTTPException(
                status_code=400,
                detail="Simbolo nao monitorado pela aplicacao.",
            )

        try:
            cotacoes_api = container.market_provider.fetch_quotes()
        except MarketProviderError as exc:
            raise HTTPException(
                status_code=502,
                detail="Falha ao consultar a API de mercado.",
            ) from exc

        payload = cotacoes_api.get(requisicao.simbolo)
        if payload is None:
            raise HTTPException(
                status_code=502,
                detail="A API de mercado nao retornou a moeda solicitada.",
            )

        container.redis_repo.set_quote(
            requisicao.simbolo,
            payload,
            container.settings.redis_ttl_seconds,
        )

    return CotacaoCacheRespostaDTO.model_validate(payload)
