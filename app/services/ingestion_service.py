from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any

from app.db.cassandra_conn import CassandraRepository
from app.db.mongo_conn import MongoRepository
from app.db.neo4j_conn import Neo4jRepository
from app.db.redis_conn import RedisRepository
from app.services.market_provider import AwesomeMarketProvider

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(
        self,
        symbols: list[str],
        redis_ttl_seconds: int,
        redis_repo: RedisRepository,
        mongo_repo: MongoRepository,
        cassandra_repo: CassandraRepository,
        neo4j_repo: Neo4jRepository,
        market_provider: AwesomeMarketProvider,
    ) -> None:
        self._symbols = symbols
        self._redis_ttl_seconds = redis_ttl_seconds
        self._redis_repo = redis_repo
        self._mongo_repo = mongo_repo
        self._cassandra_repo = cassandra_repo
        self._neo4j_repo = neo4j_repo
        self._market_provider = market_provider

    def run_cycle(self, forcar_consulta_api: bool = False) -> dict[str, Any]:
        cycle_started_at = datetime.now(UTC)
        summary: dict[str, Any] = {
            "timestamp": cycle_started_at.isoformat(),
            "cache": {},
            "mongo_writes": 0,
            "cassandra_writes": 0,
            "alerts": {},
        }

        logger.info("Consultando cotacoes do mercado tradicional...")

        cached_quotes: dict[str, dict[str, Any]] = {}
        missing_symbols: list[str] = []

        if forcar_consulta_api:
            missing_symbols = list(self._symbols)
            for symbol in self._symbols:
                summary["cache"][symbol] = "api_forcada"
                logger.info("[REDIS] Consulta forcada da API para %s", symbol)
        else:
            for symbol in self._symbols:
                cached_payload = self._redis_repo.get_quote(symbol)
                if cached_payload:
                    summary["cache"][symbol] = "hit"
                    cached_quotes[symbol] = cached_payload
                    logger.info("[REDIS] Cache Hit para %s", symbol)
                else:
                    summary["cache"][symbol] = "miss"
                    missing_symbols.append(symbol)
                    logger.info("[REDIS] Cache Miss para %s", symbol)

        fetched_quotes: dict[str, dict[str, Any]] = {}
        if missing_symbols:
            api_quotes = self._market_provider.fetch_quotes()
            for symbol in missing_symbols:
                fresh_quote = api_quotes[symbol]
                self._redis_repo.set_quote(symbol, fresh_quote, self._redis_ttl_seconds)
                fetched_quotes[symbol] = fresh_quote
                logger.info("[REDIS] Cache atualizado para %s", symbol)

        for symbol in self._symbols:
            quote = cached_quotes.get(symbol) or fetched_quotes.get(symbol)
            if quote is None:
                logger.warning("Cotacao ausente para %s no ciclo atual", symbol)
                continue

            collected_at = datetime.now(UTC)
            datalake_doc = {
                "Moeda": symbol,
                "Valor": quote["valor"],
                "Variacao": quote["variacao"],
                "data_coleta": collected_at,
                "fonte": quote["fonte"],
                "origem_preco": summary["cache"][symbol],
                "payload_api": quote["payload_api"],
                "data_api": quote.get("data_api"),
            }

            self._mongo_repo.insert_raw(datalake_doc)
            summary["mongo_writes"] += 1
            logger.info("[MONGO] Payload bruto salvo para %s", symbol)

            self._cassandra_repo.insert_price(
                symbol=symbol,
                value=quote["valor"],
                variation=quote["variacao"],
                collected_at=collected_at,
                source=quote["fonte"],
            )
            summary["cassandra_writes"] += 1
            logger.info("[CASSANDRA] Serie temporal atualizada para %s", symbol)

            investors = self._neo4j_repo.get_investors_for_symbol(symbol)
            self._neo4j_repo.mark_last_notification(symbol, investors, collected_at)
            summary["alerts"][symbol] = investors
            logger.info("[NEO4J] Investidores para %s: %s", symbol, ", ".join(investors))

        return summary
