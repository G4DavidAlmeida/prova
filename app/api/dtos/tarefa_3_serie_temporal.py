from __future__ import annotations

from pydantic import BaseModel, Field


class ConsultaSerieTemporalRequisicaoDTO(BaseModel):
    simbolo: str = Field(
        description="Simbolo da moeda no formato AAA-BBB.",
        pattern=r"^[A-Z]{3}-[A-Z]{3}$",
    )
    limite: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Quantidade maxima de pontos da serie temporal.",
    )


class RegistroSerieTemporalRespostaDTO(BaseModel):
    moeda: str = Field(description="Moeda da serie temporal.")
    data_coleta: str = Field(description="Momento da coleta da cotacao.")
    valor: str = Field(description="Valor da cotacao no instante coletado.")
    variacao: str = Field(description="Variacao da cotacao no instante coletado.")
    fonte: str = Field(description="Fonte do dado armazenado.")


class ConsultaSerieTemporalRespostaDTO(BaseModel):
    quantidade: int = Field(description="Quantidade de pontos retornados.")
    itens: list[RegistroSerieTemporalRespostaDTO] = Field(
        description="Pontos da serie temporal ordenados por data de coleta descrescente."
    )
