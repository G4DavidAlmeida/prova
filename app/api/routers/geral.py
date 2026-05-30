from __future__ import annotations

from typing import Literal

from fastapi import APIRouter

from app.api.dependencies import AppContainerDep
from app.api.dtos.geral import DependenciasSaudeDTO, RaizRespostaDTO, SaudeRespostaDTO

router = APIRouter(tags=["Geral"])


@router.get(
    "/",
    summary="Informacoes iniciais da API",
    description="Retorna uma mensagem de boas-vindas e o caminho da documentacao Swagger.",
)
def obter_raiz() -> RaizRespostaDTO:
    return RaizRespostaDTO(
        mensagem="API de monitoramento de mercado com NoSQL.",
        documentacao="/docs",
    )


@router.get(
    "/saude",
    summary="Verificar saude da aplicacao",
    description="Consulta o estado de conexao com Redis, MongoDB, Cassandra e Neo4j.",
)
def obter_saude(container: AppContainerDep) -> SaudeRespostaDTO:
    dependencias = DependenciasSaudeDTO(
        redis=bool(container.redis_repo.ping()),
        mongo=bool(container.mongo_repo.ping()),
        cassandra=bool(container.cassandra_repo.ping()),
        neo4j=bool(container.neo4j_repo.ping()),
    )

    status: Literal["ok", "degradado"] = (
        "ok" if all(dependencias.model_dump().values()) else "degradado"
    )
    return SaudeRespostaDTO(status=status, dependencias=dependencias)
