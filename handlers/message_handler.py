from __future__ import annotations

import json
import logging
from typing import Optional, Any, Protocol

from clients.backend_client import BackendClient


class WebSocketPublisherProtocol(Protocol):
    def publish(self, topic: str, payload: object) -> None: ...


class MessageHandler:
    def __init__(
        self,
        logger: logging.Logger,
        ws_publisher: Optional[WebSocketPublisherProtocol] = None,
        backend_client: Optional[BackendClient] = None,
    ) -> None:
        self._logger = logger
        self._ws_publisher = ws_publisher
        self._backend_client = backend_client

    def handle(self, topic: str, payload: bytes) -> None:
        topic_parts = _split_topic(topic)
        if not _is_empresas_topic(topic_parts):
            return

        text = payload.decode("utf-8", errors="replace")
        self._logger.info("MQTT message received topic=%s payload=%s", topic, text)

        parsed = _try_parse_json(text)
        outbound_payload = parsed if parsed is not None else text

        if _is_pantalla_topic(topic):
            if self._ws_publisher is not None:
                self._ws_publisher.publish(topic, outbound_payload)
            return

        if _is_status_topic(topic_parts) and self._backend_client is not None:
            base_topic = _strip_status_suffix(topic_parts)
            if base_topic:
                self._backend_client.send_physical_status(base_topic, outbound_payload)


def _is_pantalla_topic(topic: str) -> bool:
    segments = _split_topic(topic)
    return _is_empresas_topic(segments) and "PANTALLA" in segments


def _is_status_topic(segments: list[str]) -> bool:
    return _is_empresas_topic(segments) and segments[-1] == "status"


def _is_empresas_topic(segments: list[str]) -> bool:
    return bool(segments) and segments[0] == "empresas"


def _strip_status_suffix(segments: list[str]) -> str:
    if not segments or segments[-1] != "status":
        return "/".join(segments)
    return "/".join(segments[:-1])


def _split_topic(topic: str) -> list[str]:
    return [segment for segment in topic.split("/") if segment]


def _try_parse_json(text: str) -> Optional[Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
