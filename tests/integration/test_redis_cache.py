from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient


@pytest.mark.usefixtures("mock_market_provider")
def test_cache_miss_then_hit(
    client: TestClient,
    container: Any,
) -> None:
    first_response = client.post("/monitoramento/executar-ciclo")
    assert first_response.status_code == 200
    first_payload = first_response.json()

    assert first_payload["cache"]["USD-BRL"] == "miss"
    assert first_payload["cache"]["EUR-BRL"] == "miss"

    second_response = client.post("/monitoramento/executar-ciclo")
    assert second_response.status_code == 200
    second_payload = second_response.json()

    assert second_payload["cache"]["USD-BRL"] == "hit"
    assert second_payload["cache"]["EUR-BRL"] == "hit"

    cached_usd = container.redis_repo.get_quote("USD-BRL")
    assert cached_usd is not None
    assert cached_usd["valor"] == "5.1000"


@pytest.mark.usefixtures("mock_market_provider")
def test_tarefa_1_faz_fallback_para_api_quando_cache_miss(
    client: TestClient,
    container: Any,
) -> None:
    assert container.redis_repo.get_quote("USD-BRL") is None

    response = client.get("/tarefa-1/cache/USD-BRL")
    assert response.status_code == 200

    payload = response.json()
    assert payload["moeda"] == "USD-BRL"
    assert payload["valor"] == "5.1000"

    cached_usd = container.redis_repo.get_quote("USD-BRL")
    assert cached_usd is not None
    assert cached_usd["valor"] == "5.1000"
