from __future__ import annotations

import json
import logging
from typing import Optional, Any, Protocol

from clients.http_client import WebhookClient


class WebSocketPublisherProtocol(Protocol):
    def publish(self, topic: str, payload: object) -> None: ...


class MessageHandler:
    def __init__(
        self,
        webhook_client: WebhookClient,
        logger: logging.Logger,
        ws_publisher: Optional[WebSocketPublisherProtocol] = None,
    ) -> None:
        self._webhook_client = webhook_client
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

        endpoint_path = _endpoint_path_from_topic(topic)
        screen_name = _screen_name_from_topic(topic)
        if parsed is None:
            envelope = {
                "path": endpoint_path,
                "screen_name": screen_name,
                "payload_raw": text,
            }
        else:
            envelope = {
                "path": endpoint_path,
                "screen_name": screen_name,
                "payload": parsed,
            }

        self._webhook_client.post_json(endpoint_path, envelope)


def _is_valid_topic(topic: str) -> bool:
    segments = topic.split("/")
    return "PANTALLA" in segments


def _endpoint_path_from_topic(topic: str) -> str:
    segments = topic.split("/")
    if len(segments) <= 1:
        return ""
    return "/".join(segments[:-1])


def _screen_name_from_topic(topic: str) -> str:
    segments = topic.split("/")
    if not segments:
        return ""
    return segments[-1]


def _try_parse_json(text: str) -> Optional[Any]:
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return None
