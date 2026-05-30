from __future__ import annotations

from decimal import Decimal, InvalidOperation
from typing import Any

import requests


class MarketProviderError(RuntimeError):
    pass


class AwesomeMarketProvider:
    def __init__(self, base_url: str, symbols: list[str], timeout_seconds: int) -> None:
        self._base_url = base_url
        self._symbols = symbols
        self._timeout_seconds = timeout_seconds
        self._session = requests.Session()

    def fetch_quotes(self) -> dict[str, dict[str, Any]]:
        try:
            response = self._session.get(self._base_url, timeout=self._timeout_seconds)
            response.raise_for_status()
            payload = response.json()
        except requests.RequestException as exc:
            raise MarketProviderError("Failed to fetch market data") from exc

        quotes: dict[str, dict[str, Any]] = {}
        for symbol in self._symbols:
            provider_key = symbol.replace("-", "")
            raw_item = payload.get(provider_key)
            if not raw_item:
                continue

            value = self._normalize_number(raw_item.get("bid"))
            variation_source = raw_item.get("pctChange") or raw_item.get("varBid") or "0"
            variation = self._normalize_number(variation_source)

            quotes[symbol] = {
                "moeda": symbol,
                "valor": value,
                "variacao": variation,
                "fonte": "awesomeapi",
                "payload_api": raw_item,
                "data_api": raw_item.get("create_date"),
            }

        missing = [symbol for symbol in self._symbols if symbol not in quotes]
        if missing:
            missing_str = ", ".join(missing)
            raise MarketProviderError(f"Missing symbols in provider response: {missing_str}")

        return quotes

    @staticmethod
    def _normalize_number(value: Any) -> str:
        try:
            return format(Decimal(str(value)), "f")
        except (InvalidOperation, TypeError, ValueError) as exc:
            raise MarketProviderError(f"Invalid numeric value from provider: {value}") from exc
