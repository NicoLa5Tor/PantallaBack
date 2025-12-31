from __future__ import annotations

import threading

from config.settings import load_settings
from clients.mqtt_client import MQTTClient
from handlers.message_handler import MessageHandler
from services.mqtt_forwarder import MqttForwarderService
from services.websocket_app import create_app
from services.websocket_hub import WebSocketHub
from utils.logger import setup_logging

_mqtt_thread: threading.Thread | None = None


def _start_mqtt() -> None:
    global _mqtt_thread
    if _mqtt_thread is not None and _mqtt_thread.is_alive():
        return

    handler = MessageHandler(logger, ws_hub)
    mqtt_client = MQTTClient(settings, handler, logger)
    service = MqttForwarderService(mqtt_client, logger)

    _mqtt_thread = threading.Thread(target=service.run, daemon=True)
    _mqtt_thread.start()


logger = setup_logging()
settings = load_settings()
ws_hub = WebSocketHub(logger)
app = create_app(ws_hub, logger)
app.add_event_handler("startup", _start_mqtt)
