from __future__ import annotations

from pydantic import BaseModel, Field


class ConsultaAlertasRequisicaoDTO(BaseModel):
    simbolo: str = Field(
        description="Simbolo da moeda no formato AAA-BBB.",
        pattern=r"^[A-Z]{3}-[A-Z]{3}$",
    )


class ConsultaAlertasRespostaDTO(BaseModel):
    simbolo: str = Field(description="Moeda consultada no grafo.")
    quantidade: int = Field(description="Quantidade de investidores encontrados.")
    investidores: list[str] = Field(description="Lista de investidores a serem notificados.")
