from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.mark.usefixtures("mock_market_provider")
def test_full_cycle_writes_to_all_datastores(
    client: TestClient,
) -> None:
    run_response = client.post("/monitoramento/executar-ciclo")
    assert run_response.status_code == 200

    cycle_payload = run_response.json()
    assert cycle_payload["escritas_mongo"] == 2
    assert cycle_payload["escritas_cassandra"] == 2

    cache_response = client.get("/tarefa-1/cache/USD-BRL")
    assert cache_response.status_code == 200

    mongo_response = client.get(
        "/tarefa-2/datalake/ultimos",
        params={"simbolo": "USD-BRL", "limite": 1},
    )
    assert mongo_response.status_code == 200
    assert mongo_response.json()["quantidade"] == 1

    cassandra_response = client.get(
        "/tarefa-3/serie-temporal/ultimos",
        params={"simbolo": "USD-BRL", "limite": 1},
    )
    assert cassandra_response.status_code == 200
    assert cassandra_response.json()["quantidade"] == 1

    neo4j_response = client.get("/tarefa-4/alertas/USD-BRL")
    assert neo4j_response.status_code == 200
    assert neo4j_response.json()["quantidade"] >= 3
