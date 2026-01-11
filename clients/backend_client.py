from __future__ import annotations

import json
import logging
from typing import Dict
from urllib import error, request
from urllib.parse import urljoin


class BackendClient:
    def __init__(
        self,
        base_url: str | None,
        endpoint_url: str | None,
        token_header: str,
        token: str,
        logger: logging.Logger,
    ) -> None:
        if endpoint_url:
            self._url = endpoint_url
        elif base_url:
            self._url = urljoin(
                base_url.rstrip("/") + "/", "api/hardware/physical-status"
            )
        else:
            raise ValueError("backend url is required")
        self._token_header = token_header
        self._token = token
        self._logger = logger
        self._logger.info("Backend status endpoint: %s", self._url)

    def send_physical_status(self, topic: str, physical_status: object) -> None:
        data = _build_body(topic, physical_status)
        req = request.Request(self._url, data=data, method="PUT")
        req.add_header("Content-Type", "application/json")
        req.add_header(self._token_header, self._token)
        try:
            with request.urlopen(req, timeout=10) as response:
                response.read()
                self._logger.info(
                    "Backend status sent (%s)", response.status
                )
        except error.HTTPError as exc:
            self._logger.error(
                "Backend PUT failed (%s): %s", exc.code, exc.reason
            )
        except Exception:
            self._logger.exception("Backend PUT failed")


def _build_body(topic: str, physical_status: object) -> bytes:
    body: Dict[str, object] = {
        "topic": topic,
        "physical_status": physical_status,
    }
    return json.dumps(body).encode("utf-8")

