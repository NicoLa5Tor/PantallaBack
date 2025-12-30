from __future__ import annotations

import json
import logging
from typing import Optional, Any, Protocol


class WebSocketPublisherProtocol(Protocol):
    def publish(self, topic: str, payload: object) -> None: ...


class MessageHandler:
    def __init__(
        self,
        logger: logging.Logger,
        ws_publisher: Optional[WebSocketPublisherProtocol] = None,
    ) -> None:
        self._logger = logger
        self._ws_publisher = ws_publisher

    def handle(self, topic: str, payload: bytes) -> None:
        if not _is_valid_topic(topic):
            return

        text = payload.decode("utf-8", errors="replace")
        self._logger.info("MQTT message received topic=%s payload=%s", topic, text)

        parsed = _try_parse_json(text)
        ws_payload = parsed if parsed is not None else text
        if self._ws_publisher is not None:
            self._ws_publisher.publish(topic, ws_payload)


def _is_valid_topic(topic: str) -> bool:
    segments = topic.split("/")
    return "PANTALLA" in segments




def _try_parse_json(text: str) -> Optional[Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
