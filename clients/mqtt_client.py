from __future__ import annotations

import logging
import time
from typing import Protocol

import paho.mqtt.client as mqtt

from config.settings import Settings
from utils.backoff import Backoff


class MessageHandlerProtocol(Protocol):
    def handle(self, topic: str, payload: bytes) -> None: ...


class MQTTClient:
    def __init__(
        self,
        settings: Settings,
        handler: MessageHandlerProtocol,
        logger: logging.Logger,
    ) -> None:
        self._settings = settings
        self._handler = handler
        self._logger = logger
        self._client = mqtt.Client(client_id=settings.mqtt_client_id, clean_session=True)

        if settings.mqtt_username and settings.mqtt_password:
            self._client.username_pw_set(settings.mqtt_username, settings.mqtt_password)

        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.on_disconnect = self._on_disconnect

    def start(self) -> None:
        backoff = Backoff()
        while True:
            try:
                self._logger.info(
                    "Connecting to MQTT broker %s:%s",
                    self._settings.mqtt_broker,
                    self._settings.mqtt_port,
                )
                self._client.connect(
                    self._settings.mqtt_broker,
                    self._settings.mqtt_port,
                    keepalive=self._settings.mqtt_keep_alive,
                )
                backoff.reset()
                self._client.loop_forever()
                delay = backoff.next_delay()
                self._logger.warning(
                    "MQTT loop ended; reconnecting in %.1f seconds", delay
                )
                time.sleep(delay)
            except Exception:
                delay = backoff.next_delay()
                self._logger.exception(
                    "MQTT connection loop failed; retrying in %.1f seconds", delay
                )
                time.sleep(delay)

    def _on_connect(self, client: mqtt.Client, userdata: object, flags: dict, rc: int) -> None:
        if rc == 0:
            topic_filter = "#"
            client.subscribe(topic_filter)
            self._logger.info("Subscribed to %s", topic_filter)
        else:
            self._logger.error("MQTT connect failed with code %s", rc)

    def _on_message(self, client: mqtt.Client, userdata: object, msg: mqtt.MQTTMessage) -> None:
        self._handler.handle(msg.topic, msg.payload)

    def _on_disconnect(self, client: mqtt.Client, userdata: object, rc: int) -> None:
        if rc != 0:
            self._logger.warning("MQTT disconnected unexpectedly (rc=%s)", rc)
