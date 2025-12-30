import threading

import uvicorn

from config.settings import load_settings
from clients.http_client import WebhookClient
from clients.mqtt_client import MQTTClient
from handlers.message_handler import MessageHandler
from services.mqtt_forwarder import MqttForwarderService
from services.websocket_app import create_app
from services.websocket_hub import WebSocketHub
from utils.logger import setup_logging


def main() -> None:
    logger = setup_logging()
    settings = load_settings()

    webhook_client = WebhookClient(settings.webhook_base_url, logger)
    ws_hub = WebSocketHub(logger)
    handler = MessageHandler(webhook_client, logger, ws_hub)
    mqtt_client = MQTTClient(settings, handler, logger)

    service = MqttForwarderService(mqtt_client, logger)
    mqtt_thread = threading.Thread(target=service.run, daemon=True)
    mqtt_thread.start()

    app = create_app(ws_hub, logger)
    uvicorn.run(app, host=settings.ws_host, port=settings.ws_port, log_level="info")


if __name__ == "__main__":
    main()
