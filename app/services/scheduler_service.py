# pylint: disable=broad-exception-caught

from __future__ import annotations

import asyncio
import logging
from collections.abc import Callable
from typing import Any

logger = logging.getLogger(__name__)


class MonitorScheduler:
    def __init__(self, interval_seconds: int, run_cycle: Callable[[], dict[str, Any]]) -> None:
        self._interval_seconds = interval_seconds
        self._run_cycle = run_cycle
        self._stop_event = asyncio.Event()
        self._task: asyncio.Task[None] | None = None

    def start(self) -> None:
        if self._task and not self._task.done():
            return
        self._stop_event.clear()
        self._task = asyncio.create_task(self._loop(), name="market-monitor-loop")

    async def stop(self) -> None:
        self._stop_event.set()
        if self._task is not None:
            await self._task
            self._task = None

    async def _loop(self) -> None:
        while not self._stop_event.is_set():
            try:
                summary = await asyncio.to_thread(self._run_cycle)
                logger.info("Ciclo concluido: %s", summary)
            except Exception:  # noqa: BLE001
                logger.exception("Falha no ciclo de monitoramento")

            try:
                await asyncio.wait_for(
                    self._stop_event.wait(),
                    timeout=self._interval_seconds,
                )
            except asyncio.TimeoutError:
                continue
