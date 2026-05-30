from __future__ import annotations

from fastapi.testclient import TestClient


def test_neo4j_returns_investors_for_symbol(client: TestClient) -> None:
    response = client.get("/tarefa-4/alertas/USD-BRL")
    assert response.status_code == 200

    payload = response.json()
    assert payload["simbolo"] == "USD-BRL"
    assert payload["quantidade"] >= 3
    assert "Alice" in payload["investidores"]
