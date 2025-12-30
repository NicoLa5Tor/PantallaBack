from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
import logging
from typing import Dict, Optional

from fastapi import WebSocket


@dataclass(frozen=True)
class OutboundMessage:
    topic: str
    payload: object
    timestamp: str


class WebSocketHub:
    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._clients: Dict[WebSocket, str] = {}
        self._lock = asyncio.Lock()

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        self._loop = loop

    async def register(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._clients[websocket] = ""

    async def unregister(self, websocket: WebSocket) -> None:
        async with self._lock:
            self._clients.pop(websocket, None)

    async def set_subscription(self, websocket: WebSocket, topic: str) -> None:
        async with self._lock:
            self._clients[websocket] = topic

    def publish(self, topic: str, payload: object) -> None:
        if self._loop is None:
            return
        asyncio.run_coroutine_threadsafe(
            self._broadcast(topic, payload), self._loop
        )

    async def _broadcast(self, topic: str, payload: object) -> None:
        timestamp = datetime.now(timezone.utc).isoformat()
        async with self._lock:
            targets = list(self._clients.items())

        for websocket, subscribed_topic in targets:
            if not _matches_subscription(topic, subscribed_topic):
                continue
            try:
                message = OutboundMessage(
                    topic=subscribed_topic,
                    payload=payload,
                    timestamp=timestamp,
                )
                await websocket.send_json(message.__dict__)
            except Exception:
                self._logger.exception("WebSocket send failed")


def _matches_subscription(full_topic: str, subscription: str) -> bool:
    if not subscription:
        return False
    if full_topic == subscription:
        return True
    return full_topic.startswith(f"{subscription}/")
