import asyncio
import hashlib
import json
import logging
from collections.abc import Callable
from enum import StrEnum

from fastapi import Request
from sse_starlette.sse import EventSourceResponse, ServerSentEvent

from flux_watch_api.core.config import AppConfig
from flux_watch_api.core.registry import registry

logger = logging.getLogger(__name__)


class Event(StrEnum):
    UPDATE = "update"


class ServerSentEvents:
    def __init__(self):
        self.config: AppConfig = registry.resolve(AppConfig)

    async def _stream_generator(self, fn: Callable, args: dict, request: Request):
        prev_hash: str | None = None

        while True:
            if await request.is_disconnected():
                logger.debug("SSE request disconnected")
                break

            data = await asyncio.to_thread(fn, **args)
            data_json = json.dumps(data, sort_keys=True, default=str)
            current_hash = hashlib.sha256(data_json.encode()).hexdigest()

            if current_hash != prev_hash:
                yield ServerSentEvent(data=data_json, event=Event.UPDATE, id=current_hash)
                prev_hash = current_hash
                logger.debug(f"New SSE response: {data_json}")
            else:
                logger.debug("No change in status")

            await asyncio.sleep(self.config.STREAM_DELAY)

    async def stream(self, fn: Callable, args: dict, request: Request):
        return EventSourceResponse(self._stream_generator(fn, args, request))
