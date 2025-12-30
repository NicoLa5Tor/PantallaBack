from __future__ import annotations

from typing import Any
import logging
from urllib.parse import urljoin

import requests


class WebhookClient:
    def __init__(self, webhook_url: str, logger: logging.Logger, timeout: int = 10) -> None:
        self._webhook_base_url = webhook_url.rstrip("/")
        self._logger = logger
        self._timeout = timeout
        self._session = requests.Session()

    def post_json(self, endpoint_path: str, payload: Any) -> None:
        url = _build_url(self._webhook_base_url, endpoint_path)
        try:
            response = self._session.post(
                url, json=payload, timeout=self._timeout
            )
            response.raise_for_status()
        except requests.RequestException:
            self._logger.exception("Webhook JSON post failed")


def _build_url(base_url: str, endpoint_path: str) -> str:
    clean_path = endpoint_path.lstrip("/")
    return urljoin(f"{base_url}/", clean_path)
