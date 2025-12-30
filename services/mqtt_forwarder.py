from __future__ import annotations

import logging

from clients.mqtt_client import MQTTClient


class MqttForwarderService:
    def __init__(self, mqtt_client: MQTTClient, logger: logging.Logger) -> None:
        self._mqtt_client = mqtt_client
        self._logger = logger

    def run(self) -> None:
        self._logger.info("Starting MQTT forwarder service")
        self._mqtt_client.start()
