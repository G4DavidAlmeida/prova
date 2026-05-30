from __future__ import annotations

import pytest
from fastapi.testclient import TestClient


@pytest.mark.usefixtures("mock_market_provider")
def test_mongo_saves_raw_payload(client: TestClient) -> None:
    run_response = client.post("/monitoramento/executar-ciclo")
    assert run_response.status_code == 200

    response = client.get(
        "/tarefa-2/datalake/ultimos",
        params={"simbolo": "USD-BRL", "limite": 1},
    )
    assert response.status_code == 200

    payload = response.json()
    assert payload["quantidade"] == 1

    item = payload["itens"][0]
    assert item["moeda"] == "USD-BRL"
    assert item["valor"] == "5.1000"
    assert "data_coleta" in item
    assert "payload_api" in item
