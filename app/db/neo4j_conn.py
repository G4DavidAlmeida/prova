from __future__ import annotations

from datetime import datetime

from neo4j import Driver, GraphDatabase
from neo4j.exceptions import Neo4jError, ServiceUnavailable

from app.core.settings import Settings


class Neo4jRepository:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._driver: Driver | None = None

    @property
    def driver(self) -> Driver:
        if self._driver is None:
            raise RuntimeError("Neo4j driver is not connected")
        return self._driver

    def connect(self) -> None:
        self._driver = GraphDatabase.driver(
            self._settings.neo4j_uri,
            auth=(self._settings.neo4j_user, self._settings.neo4j_password),
        )
        self._driver.verify_connectivity()

    def ping(self) -> bool:
        try:
            self.driver.verify_connectivity()
            return True
        except (ServiceUnavailable, Neo4jError, RuntimeError):
            return False

    def seed_investors(self, investors: list[str], symbols: list[str]) -> None:
        query = """
        UNWIND $investors AS investor_name
        MERGE (i:Investidor {nome: investor_name})
        WITH i
        UNWIND $symbols AS symbol
        MERGE (m:Moeda {codigo: symbol})
        MERGE (i)-[:ACOMPANHA]->(m)
        """
        with self.driver.session(database=self._settings.neo4j_database) as session:
            session.run(query, investors=investors, symbols=symbols)

    def get_investors_for_symbol(self, symbol: str) -> list[str]:
        query = """
        MATCH (i:Investidor)-[:ACOMPANHA]->(m:Moeda {codigo: $symbol})
        RETURN i.nome AS nome
        ORDER BY i.nome
        """
        with self.driver.session(database=self._settings.neo4j_database) as session:
            result = session.run(query, symbol=symbol.upper())
            return [record["nome"] for record in result]

    def mark_last_notification(
        self,
        symbol: str,
        investors: list[str],
        timestamp: datetime,
    ) -> int:
        query = """
        MATCH (i:Investidor)-[r:ACOMPANHA]->(m:Moeda {codigo: $symbol})
        WHERE i.nome IN $investors
        SET r.ultima_notificacao = $timestamp
        RETURN count(r) AS updated
        """
        with self.driver.session(database=self._settings.neo4j_database) as session:
            row = session.run(
                query,
                symbol=symbol.upper(),
                investors=investors,
                timestamp=timestamp.isoformat(),
            ).single()
            if row is None:
                return 0
            return int(row["updated"])

    def clear_alert_graph(self) -> None:
        with self.driver.session(database=self._settings.neo4j_database) as session:
            session.run("MATCH (i:Investidor)-[r:ACOMPANHA]->(m:Moeda) DELETE r")
            session.run("MATCH (i:Investidor) DELETE i")
            session.run("MATCH (m:Moeda) DELETE m")

    def close(self) -> None:
        if self._driver is not None:
            self._driver.close()
            self._driver = None
