from __future__ import annotations

import os
import socket
from collections.abc import Generator
from typing import Any

import pytest
from fastapi.testclient import TestClient

DEFAULT_TEST_ENV = {
    "MONITOR_ENABLED": "false",
    "REDIS_HOST": "localhost",
    "REDIS_PORT": "6379",
    "MONGO_HOST": "localhost",
    "MONGO_PORT": "27017",
    "MONGO_USER": "root",
    "MONGO_PASSWORD": "password",
    "CASSANDRA_HOSTS": "localhost",
    "CASSANDRA_PORT": "9042",
    "NEO4J_URI": "bolt://localhost:7687",
    "NEO4J_USER": "neo4j",
    "NEO4J_PASSWORD": "password",
    "SYMBOLS": "USD-BRL,EUR-BRL",
}

REQUIRED_SERVICES = [
    ("redis", "localhost", 6379),
    ("mongo", "localhost", 27017),
    ("cassandra", "localhost", 9042),
    ("neo4j", "localhost", 7687),
]

for env_key, env_value in DEFAULT_TEST_ENV.items():
    os.environ.setdefault(env_key, env_value)


def _is_port_open(host: str, port: int, timeout_seconds: float = 0.5) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(timeout_seconds)
        return sock.connect_ex((host, port)) == 0


def _assert_services_available() -> None:
    unavailable = [
        name
        for name, host, port in REQUIRED_SERVICES
        if not _is_port_open(host, port)
    ]
    if unavailable:
        services = ", ".join(unavailable)
        pytest.skip(f"Integration services are unavailable: {services}")


@pytest.fixture(scope="session", name="test_client")
def fixture_test_client() -> Generator[TestClient, None, None]:
    _assert_services_available()

    from app.core.settings import get_settings

    get_settings.cache_clear()

    from app.main import create_app

    app_instance = create_app()

    with TestClient(app_instance) as test_client_instance:
        yield test_client_instance


@pytest.fixture(scope="session", name="container")
def fixture_container(test_client: Any) -> Any:
    return test_client.app.state.container


@pytest.fixture(name="client")
def fixture_client(test_client: TestClient) -> TestClient:
    return test_client


@pytest.fixture(autouse=True)
def fixture_reset_databases(container: Any) -> None:
    container.redis_repo.flush()
    container.mongo_repo.reset_collection()
    container.cassandra_repo.truncate_table()
    container.neo4j_repo.clear_alert_graph()
    container.seed_service.seed()


@pytest.fixture(name="fixed_quotes")
def fixture_fixed_quotes() -> dict[str, dict[str, Any]]:
    return {
        "USD-BRL": {
            "moeda": "USD-BRL",
            "valor": "5.1000",
            "variacao": "0.1500",
            "fonte": "awesomeapi",
            "payload_api": {
                "code": "USD",
                "bid": "5.1000",
                "pctChange": "0.1500",
                "create_date": "2026-05-30 12:00:00",
            },
            "data_api": "2026-05-30 12:00:00",
        },
        "EUR-BRL": {
            "moeda": "EUR-BRL",
            "valor": "5.6500",
            "variacao": "0.2100",
            "fonte": "awesomeapi",
            "payload_api": {
                "code": "EUR",
                "bid": "5.6500",
                "pctChange": "0.2100",
                "create_date": "2026-05-30 12:00:00",
            },
            "data_api": "2026-05-30 12:00:00",
        },
    }


@pytest.fixture(name="mock_market_provider")
def fixture_mock_market_provider(
    container: Any,
    monkeypatch: pytest.MonkeyPatch,
    fixed_quotes: dict[str, Any],
) -> dict[str, Any]:
    monkeypatch.setattr(container.market_provider, "fetch_quotes", lambda: fixed_quotes)
    return fixed_quotes
