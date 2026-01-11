from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Optional

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    mqtt_broker: str
    mqtt_port: int
    mqtt_username: Optional[str]
    mqtt_password: Optional[str]
    mqtt_client_id: str
    mqtt_keep_alive: int
    mqtt_topic: str
    ws_host: str
    ws_port: int
    backend_base_url: Optional[str]
    backend_status_url: Optional[str]
    backend_token: Optional[str]
    backend_token_header: Optional[str]


def _get_required(name: str) -> str:
    value = os.getenv(name)
    if value is None or value == "":
        raise ValueError(f"Missing required env var: {name}")
    return value


def load_settings() -> Settings:
    load_dotenv()

    mqtt_broker = _get_required("MQTT_BROKER")
    mqtt_port = int(_get_required("MQTT_PORT"))
    mqtt_username = os.getenv("MQTT_USERNAME") or None
    mqtt_password = os.getenv("MQTT_PASSWORD") or None
    mqtt_client_id = _get_required("MQTT_CLIENT_ID")
    mqtt_keep_alive = int(_get_required("MQTT_KEEP_ALIVE"))
    mqtt_topic = _get_required("MQTT_TOPIC")
    ws_host = os.getenv("WS_HOST") or "0.0.0.0"
    ws_port = int(os.getenv("WS_PORT") or "8000")
    backend_base_url = os.getenv("BACKEND_BASE_URL") or None
    backend_status_url = os.getenv("BACKEND_STATUS_URL") or None
    backend_token = os.getenv("BACKEND_INTERNAL_TOKEN") or os.getenv("BACKEND_STATUS_TOKEN") or None
    backend_token_header = (
        os.getenv("BACKEND_INTERNAL_TOKEN_HEADER")
        or os.getenv("BACKEND_STATUS_TOKEN_HEADER")
        or "INTERNAL_TOKEN_HEADER"
    )

    return Settings(
        mqtt_broker=mqtt_broker,
        mqtt_port=mqtt_port,
        mqtt_username=mqtt_username,
        mqtt_password=mqtt_password,
        mqtt_client_id=mqtt_client_id,
        mqtt_keep_alive=mqtt_keep_alive,
        mqtt_topic=mqtt_topic,
        ws_host=ws_host,
        ws_port=ws_port,
        backend_base_url=backend_base_url,
        backend_status_url=backend_status_url,
        backend_token=backend_token,
        backend_token_header=backend_token_header,
    )
