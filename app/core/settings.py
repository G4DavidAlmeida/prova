# pylint: disable=no-member

from functools import lru_cache
from typing import cast

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(default="FastAPI NoSQL Market Monitor", alias="APP_NAME")
    app_env: str = Field(default="dev", alias="APP_ENV")
    api_host: str = Field(default="0.0.0.0", alias="API_HOST")
    api_port: int = Field(default=8000, alias="API_PORT")
    log_level: str = Field(default="INFO", alias="LOG_LEVEL")

    poll_interval_seconds: int = Field(default=20, alias="POLL_INTERVAL_SECONDS")
    redis_ttl_seconds: int = Field(default=45, alias="REDIS_TTL_SECONDS")
    monitor_enabled: bool = Field(default=True, alias="MONITOR_ENABLED")

    market_api_url: str = Field(
        default="https://economia.awesomeapi.com.br/last/USD-BRL,EUR-BRL",
        alias="MARKET_API_URL",
    )
    symbols_raw: str = Field(default="USD-BRL,EUR-BRL", alias="SYMBOLS")
    request_timeout_seconds: int = Field(default=10, alias="REQUEST_TIMEOUT_SECONDS")

    redis_host: str = Field(default="localhost", alias="REDIS_HOST")
    redis_port: int = Field(default=6379, alias="REDIS_PORT")
    redis_db: int = Field(default=0, alias="REDIS_DB")

    mongo_host: str = Field(default="localhost", alias="MONGO_HOST")
    mongo_port: int = Field(default=27017, alias="MONGO_PORT")
    mongo_user: str = Field(default="root", alias="MONGO_USER")
    mongo_password: str = Field(default="password", alias="MONGO_PASSWORD")
    mongo_database: str = Field(default="market_intelligence", alias="MONGO_DATABASE")
    mongo_collection: str = Field(default="raw_quotes", alias="MONGO_COLLECTION")

    cassandra_hosts_raw: str = Field(default="localhost", alias="CASSANDRA_HOSTS")
    cassandra_port: int = Field(default=9042, alias="CASSANDRA_PORT")
    cassandra_keyspace: str = Field(default="market_intelligence", alias="CASSANDRA_KEYSPACE")
    cassandra_table: str = Field(default="historico_precos", alias="CASSANDRA_TABLE")

    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field(default="password", alias="NEO4J_PASSWORD")
    neo4j_database: str = Field(default="neo4j", alias="NEO4J_DATABASE")

    faker_locale: str = Field(default="pt_BR", alias="FAKER_LOCALE")
    seed_investor_count: int = Field(default=6, alias="SEED_INVESTOR_COUNT")

    @property
    def symbols(self) -> list[str]:
        symbols_raw = cast(str, self.symbols_raw)
        return [
            symbol.strip().upper()
            for symbol in symbols_raw.split(",")
            if symbol.strip()
        ]

    @property
    def cassandra_hosts(self) -> list[str]:
        cassandra_hosts_raw = cast(str, self.cassandra_hosts_raw)
        return [
            host.strip()
            for host in cassandra_hosts_raw.split(",")
            if host.strip()
        ]

    @property
    def mongo_uri(self) -> str:
        return (
            f"mongodb://{self.mongo_user}:{self.mongo_password}"
            f"@{self.mongo_host}:{self.mongo_port}/?authSource=admin"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
