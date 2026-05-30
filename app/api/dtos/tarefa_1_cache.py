from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ConsultaCacheRequisicaoDTO(BaseModel):
    simbolo: str = Field(
        description="Simbolo da moeda no formato AAA-BBB.",
        pattern=r"^[A-Z]{3}-[A-Z]{3}$",
    )


class CotacaoCacheRespostaDTO(BaseModel):
    moeda: str = Field(description="Moeda consultada.")
    valor: str = Field(description="Valor atual da cotacao.")
    variacao: str = Field(description="Variacao percentual ou absoluta retornada pela fonte.")
    fonte: str = Field(description="Fonte do dado de mercado.")
    payload_api: dict[str, Any] = Field(description="Payload bruto retornado pela API de mercado.")
    data_api: str | None = Field(default=None, description="Data informada pela API de mercado.")
