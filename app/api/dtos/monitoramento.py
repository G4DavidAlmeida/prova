from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ExecutarCicloRequisicaoDTO(BaseModel):
    forcar_consulta_api: bool = Field(
        default=False,
        description="Quando true, ignora o cache e consulta a API para todas as moedas.",
    )


class ExecutarCicloRespostaDTO(BaseModel):
    data_hora_ciclo: str = Field(description="Horario UTC de inicio do ciclo executado.")
    cache: dict[str, Literal["hit", "miss", "api_forcada"]] = Field(
        description="Resultado de cache por moeda no ciclo atual."
    )
    escritas_mongo: int = Field(description="Quantidade de registros gravados no MongoDB.")
    escritas_cassandra: int = Field(description="Quantidade de registros gravados no Cassandra.")
    alertas: dict[str, list[str]] = Field(
        description="Investidores encontrados por moeda para notificacao."
    )
