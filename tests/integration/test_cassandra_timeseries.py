from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.mark.usefixtures("mock_market_provider")
def test_cassandra_stores_time_series(client: TestClient) -> None:
    run_response = client.post("/monitoramento/executar-ciclo")
    assert run_response.status_code == 200

    response = client.get(
        "/tarefa-3/serie-temporal/ultimos",
        params={"simbolo": "USD-BRL", "limite": 5},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["quantidade"] >= 1

    first_row = payload["itens"][0]
    assert first_row["moeda"] == "USD-BRL"
    assert first_row["valor"] == "5.1000"
    assert "data_coleta" in first_row
