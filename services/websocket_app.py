from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

from fastapi import FastAPI, WebSocket, WebSocketDisconnect

from services.websocket_hub import WebSocketHub


def create_app(hub: WebSocketHub, logger: logging.Logger) -> FastAPI:
    app = FastAPI()

    @app.on_event("startup")
    async def _startup() -> None:
        hub.set_loop(asyncio.get_running_loop())

    @app.websocket("/ws")
    async def websocket_endpoint(websocket: WebSocket) -> None:
        await websocket.accept()
        await hub.register(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                await _handle_subscription_message(data, websocket, hub, logger)
        except WebSocketDisconnect:
            await hub.unregister(websocket)
        except Exception:
            logger.exception("WebSocket connection error")
            await hub.unregister(websocket)

    return app


async def _handle_subscription_message(
    data: str, websocket: WebSocket, hub: WebSocketHub, logger: logging.Logger
) -> None:
    try:
        message = json.loads(data)
    except json.JSONDecodeError:
        logger.warning("Ignoring invalid WebSocket JSON")
        return

    action = message.get("action")
    if action != "subscribe":
        logger.warning("Ignoring unsupported WebSocket action: %s", action)
        return

    topic = message.get("topic")
    if not isinstance(topic, str) or not topic:
        logger.warning("Ignoring invalid WebSocket topic")
        return

    await hub.set_subscription(websocket, topic)
