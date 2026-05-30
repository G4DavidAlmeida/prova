from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.core.settings import Settings
    from app.db.cassandra_conn import CassandraRepository
    from app.db.mongo_conn import MongoRepository
    from app.db.neo4j_conn import Neo4jRepository
    from app.db.redis_conn import RedisRepository
    from app.services.ingestion_service import IngestionService
    from app.services.market_provider import AwesomeMarketProvider
    from app.services.scheduler_service import MonitorScheduler
    from app.services.seed_service import SeedService

logger = logging.getLogger(__name__)

@dataclass
class AppContainer:
    settings: Settings
    redis_repo: RedisRepository
    mongo_repo: MongoRepository
    cassandra_repo: CassandraRepository
    neo4j_repo: Neo4jRepository
    market_provider: AwesomeMarketProvider
    ingestion_service: IngestionService
    seed_service: SeedService
    scheduler: MonitorScheduler
