# pylint: disable=no-name-in-module

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from typing import Any

from cassandra import OperationTimedOut  # type: ignore[import-untyped]
from cassandra.cluster import Cluster, NoHostAvailable, Session  # type: ignore[import-untyped,attr-defined]
from cassandra.query import dict_factory  # type: ignore[import-untyped,attr-defined]

from app.core.settings import Settings


class CassandraRepository:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._cluster: Cluster | None = None
        self._session: Session | None = None

    @property
    def session(self) -> Session:
        if self._session is None:
            raise RuntimeError("Cassandra session is not connected")
        return self._session

    def connect(self) -> None:
        self._cluster = Cluster(
            contact_points=self._settings.cassandra_hosts,
            port=self._settings.cassandra_port,
        )
        self._session = self._cluster.connect()
        self._session.row_factory = dict_factory
        self.ping()

    def ping(self) -> bool:
        try:
            row = self.session.execute("SELECT release_version FROM system.local").one()
            return row is not None
        except (NoHostAvailable, OperationTimedOut, RuntimeError):
            return False

    def setup_schema(self) -> None:
        self.session.execute(
            f"""
            CREATE KEYSPACE IF NOT EXISTS {self._settings.cassandra_keyspace}
            WITH replication = {{'class': 'SimpleStrategy', 'replication_factor': '1'}}
            """
        )
        self.session.set_keyspace(self._settings.cassandra_keyspace)
        self.session.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {self._settings.cassandra_table} (
                moeda text,
                data_coleta timestamp,
                valor decimal,
                variacao decimal,
                fonte text,
                PRIMARY KEY ((moeda), data_coleta)
            ) WITH CLUSTERING ORDER BY (data_coleta DESC)
            """
        )

    def insert_price(
        self,
        symbol: str,
        value: str,
        variation: str,
        collected_at: datetime,
        source: str,
    ) -> None:
        self.session.execute(
            f"""
            INSERT INTO {self._settings.cassandra_table}
            (moeda, data_coleta, valor, variacao, fonte)
            VALUES (%s, %s, %s, %s, %s)
            """,
            (
                symbol.upper(),
                collected_at,
                Decimal(str(value)),
                Decimal(str(variation)),
                source,
            ),
        )

    def get_latest(self, symbol: str, limit: int = 10) -> list[dict[str, Any]]:
        rows = self.session.execute(
            f"""
            SELECT moeda, data_coleta, valor, variacao, fonte
            FROM {self._settings.cassandra_table}
            WHERE moeda = %s
            LIMIT %s
            """,
            (symbol.upper(), limit),
        )
        result: list[dict[str, Any]] = []
        for row in rows:
            item = dict(row)
            item["data_coleta"] = item["data_coleta"].isoformat()
            item["valor"] = self._format_decimal(item["valor"])
            item["variacao"] = self._format_decimal(item["variacao"])
            result.append(item)
        return result

    def truncate_table(self) -> None:
        self.session.execute(f"TRUNCATE {self._settings.cassandra_table}")

    def close(self) -> None:
        if self._session is not None:
            self._session.shutdown()
            self._session = None
        if self._cluster is not None:
            self._cluster.shutdown()
            self._cluster = None

    @staticmethod
    def _format_decimal(value: Decimal) -> str:
        return format(value.quantize(Decimal("0.0001")), "f")
