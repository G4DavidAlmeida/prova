from __future__ import annotations

from datetime import datetime
from typing import Any

from pymongo import DESCENDING, MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import PyMongoError

from app.core.settings import Settings


class MongoRepository:
    def __init__(self, settings: Settings) -> None:
        self._settings = settings
        self._client: MongoClient | None = None
        self._database: Database | None = None
        self._collection: Collection | None = None

    @property
    def client(self) -> MongoClient:
        if self._client is None:
            raise RuntimeError("Mongo client is not connected")
        return self._client

    @property
    def collection(self) -> Collection:
        if self._collection is None:
            raise RuntimeError("Mongo collection is not ready")
        return self._collection

    def connect(self) -> None:
        self._client = MongoClient(self._settings.mongo_uri)
        self._client.admin.command("ping")
        self._database = self._client[self._settings.mongo_database]
        self._collection = self._database[self._settings.mongo_collection]

    def ping(self) -> bool:
        try:
            return bool(self.client.admin.command("ping").get("ok"))
        except PyMongoError:
            return False

    def insert_raw(self, payload: dict[str, Any]) -> str:
        result = self.collection.insert_one(payload)
        return str(result.inserted_id)

    def get_latest(self, symbol: str | None = None, limit: int = 10) -> list[dict[str, Any]]:
        query: dict[str, Any] = {}
        if symbol:
            query["Moeda"] = symbol.upper()
        cursor = self.collection.find(query).sort("data_coleta", DESCENDING).limit(limit)
        return [self._serialize_document(item) for item in cursor]

    def reset_collection(self) -> None:
        self.collection.drop()
        db = self.client[self._settings.mongo_database]
        self._collection = db[self._settings.mongo_collection]

    def close(self) -> None:
        if self._client is not None:
            self._client.close()
            self._client = None
            self._database = None
            self._collection = None

    @staticmethod
    def _serialize_document(document: dict[str, Any]) -> dict[str, Any]:
        clean = dict(document)
        if "_id" in clean:
            clean["_id"] = str(clean["_id"])
        if isinstance(clean.get("data_coleta"), datetime):
            clean["data_coleta"] = clean["data_coleta"].isoformat()
        return clean
