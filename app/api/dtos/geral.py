from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RaizRespostaDTO(BaseModel):
    mensagem: str = Field(description="Mensagem de boas-vindas da API.")
    documentacao: str = Field(description="Caminho relativo da documentacao Swagger.")


class DependenciasSaudeDTO(BaseModel):
    redis: bool = Field(description="Estado da conexao com Redis.")
    mongo: bool = Field(description="Estado da conexao com MongoDB.")
    cassandra: bool = Field(description="Estado da conexao com Cassandra.")
    neo4j: bool = Field(description="Estado da conexao com Neo4j.")


class SaudeRespostaDTO(BaseModel):
    status: Literal["ok", "degradado"] = Field(
        description="Status geral da API com base na disponibilidade das dependencias."
    )
    dependencias: DependenciasSaudeDTO = Field(
        description="Detalhe de conectividade para cada dependencia.")
