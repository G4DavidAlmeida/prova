from __future__ import annotations

from faker import Faker

from app.core.settings import Settings
from app.db.neo4j_conn import Neo4jRepository


class SeedService:
    BASE_NAMES = ["Alice", "Bob", "Carlos"]

    def __init__(self, settings: Settings, neo4j_repo: Neo4jRepository) -> None:
        self._settings = settings
        self._neo4j_repo = neo4j_repo
        self._faker = Faker(settings.faker_locale)

    def seed(self) -> list[str]:
        investors = self._build_investor_names(self._settings.seed_investor_count)
        self._neo4j_repo.seed_investors(investors=investors, symbols=self._settings.symbols)
        return investors

    def _build_investor_names(self, desired_count: int) -> list[str]:
        names = list(self.BASE_NAMES)
        while len(names) < desired_count:
            candidate = self._faker.first_name()
            if candidate not in names:
                names.append(candidate)
        return names
