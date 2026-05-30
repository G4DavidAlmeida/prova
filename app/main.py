from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.routes import router
from app.core.logging_config import configure_logging
from app.core.settings import Settings, get_settings
from app.db.cassandra_conn import CassandraRepository
from app.db.mongo_conn import MongoRepository
from app.db.neo4j_conn import Neo4jRepository
from app.db.redis_conn import RedisRepository
from app.dto_configs import AppContainer
from app.services.ingestion_service import IngestionService
from app.services.market_provider import AwesomeMarketProvider
from app.services.scheduler_service import MonitorScheduler
from app.services.seed_service import SeedService

logger = logging.getLogger(__name__)



def _build_container(settings: Settings) -> AppContainer:
    redis_repo = RedisRepository(settings)
    mongo_repo = MongoRepository(settings)
    cassandra_repo = CassandraRepository(settings)
    neo4j_repo = Neo4jRepository(settings)

    market_provider = AwesomeMarketProvider(
        base_url=settings.market_api_url,
        symbols=settings.symbols,
        timeout_seconds=settings.request_timeout_seconds,
    )

    ingestion_service = IngestionService(
        symbols=settings.symbols,
        redis_ttl_seconds=settings.redis_ttl_seconds,
        redis_repo=redis_repo,
        mongo_repo=mongo_repo,
        cassandra_repo=cassandra_repo,
        neo4j_repo=neo4j_repo,
        market_provider=market_provider,
    )

    seed_service = SeedService(settings=settings, neo4j_repo=neo4j_repo)
    scheduler = MonitorScheduler(
        interval_seconds=settings.poll_interval_seconds,
        run_cycle=ingestion_service.run_cycle,
    )

    return AppContainer(
        settings=settings,
        redis_repo=redis_repo,
        mongo_repo=mongo_repo,
        cassandra_repo=cassandra_repo,
        neo4j_repo=neo4j_repo,
        market_provider=market_provider,
        ingestion_service=ingestion_service,
        seed_service=seed_service,
        scheduler=scheduler,
    )


@asynccontextmanager
async def lifespan(fastapi_app: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    container = _build_container(settings)
    fastapi_app.state.container = container

    logger.info("Inicializando conexoes com os bancos NoSQL")
    container.redis_repo.connect()
    container.mongo_repo.connect()
    container.cassandra_repo.connect()
    container.cassandra_repo.setup_schema()
    container.neo4j_repo.connect()

    investors = container.seed_service.seed()
    logger.info("Seed inicial no Neo4j concluido com %s investidores", len(investors))

    if settings.monitor_enabled:
        container.scheduler.start()
        logger.info(
            "Loop de monitoramento iniciado com intervalo de %ss",
            settings.poll_interval_seconds,
        )

    try:
        yield
    finally:
        logger.info("Encerrando aplicacao")
        await container.scheduler.stop()
        container.neo4j_repo.close()
        container.cassandra_repo.close()
        container.mongo_repo.close()
        container.redis_repo.close()


def create_app() -> FastAPI:
    settings = get_settings()
    fastapi_app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        lifespan=lifespan,
    )
    fastapi_app.include_router(router)
    return fastapi_app


app = create_app()
