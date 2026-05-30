from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ConsultaDatalakeRequisicaoDTO(BaseModel):
    simbolo: str | None = Field(
        default=None,
        description="Filtro opcional de moeda no formato AAA-BBB.",
    )
    limite: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Quantidade maxima de registros retornados.",
    )


class RegistroDatalakeRespostaDTO(BaseModel):
    id_documento: str = Field(description="Identificador do documento no MongoDB.")
    moeda: str = Field(description="Moeda coletada.")
    valor: str = Field(description="Valor coletado da moeda.")
    variacao: str = Field(description="Variacao coletada da moeda.")
    data_coleta: str = Field(description="Timestamp de coleta do registro.")
    fonte: str = Field(description="Fonte do dado coletado.")
    origem_preco: str = Field(description="Origem do preco no ciclo (cache ou API).")
    payload_api: dict[str, Any] = Field(description="Documento bruto recebido da API externa.")
    data_api: str | None = Field(default=None, description="Data da cotacao informada pela API.")


class ConsultaDatalakeRespostaDTO(BaseModel):
    quantidade: int = Field(description="Quantidade de registros retornados.")
    itens: list[RegistroDatalakeRespostaDTO] = Field(description="Registros encontrados no Data Lake.")
