import logging
import time
from typing import Any

import requests

from config import settings

logger = logging.getLogger(__name__)


class ZohoAuthError(Exception):
    pass


class ZohoRateLimitError(Exception):
    pass


class ZohoAPIError(Exception):
    pass


class ZohoClient:
    def __init__(self):
        self._session = requests.Session()
        self._access_token: str | None = None
        self._token_expiry: float = 0
        self._token_lock = __import__("threading").Lock()

    def _ensure_token(self) -> None:
        if time.time() >= self._token_expiry:
            self._refresh_token()

    def _refresh_token(self) -> None:
        with self._token_lock:
            if time.time() < self._token_expiry:
                return
            url = f"https://{settings.zoho_accounts_domain}/oauth/v2/token"
            data = {
                "refresh_token": settings.zoho_refresh_token,
                "client_id": settings.zoho_client_id,
                "client_secret": settings.zoho_client_secret,
                "grant_type": "refresh_token",
            }
            resp = self._session.post(url, data=data, timeout=30)
            if resp.status_code != 200:
                raise ZohoAuthError(
                    f"Token refresh failed: HTTP {resp.status_code}"
                )
            body = resp.json()
            self._access_token = body["access_token"]
            self._token_expiry = time.time() + body["expires_in_sec"] - 60

    def get_records(
        self, report_name: str, params: dict[str, Any] | None = None
    ) -> list[dict[str, Any]]:
        all_records: list[dict[str, Any]] = []
        path = (
            f"data/{settings.zoho_owner}/{settings.zoho_app_name}"
            f"/report/{report_name}"
        )
        while path:
            data = self._request_with_retry("GET", path, params=params)
            params = None
            records = data.get("data", [])
            all_records.extend(records)
            path = data.get("record_cursor")
        return all_records

    def get_record(
        self, report_name: str, record_id: str
    ) -> dict[str, Any]:
        path = (
            f"data/{settings.zoho_owner}/{settings.zoho_app_name}"
            f"/report/{report_name}/{record_id}"
        )
        return self._request_with_retry("GET", path)

    def _request_with_retry(
        self, method: str, path: str, **kwargs: Any
    ) -> dict[str, Any]:
        max_retries = 3
        for attempt in range(max_retries + 1):
            try:
                return self._request(method, path, **kwargs)
            except ZohoAuthError:
                if attempt < max_retries:
                    self._access_token = None
                    self._token_expiry = 0
                    self._ensure_token()
                    continue
                raise
            except ZohoRateLimitError:
                if attempt < max_retries:
                    sleep_time = 2 ** attempt
                    logger.info(
                        "Rate limited, retrying in %ds", sleep_time
                    )
                    time.sleep(sleep_time)
                    continue
                raise
            except requests.exceptions.Timeout:
                if attempt < max_retries:
                    sleep_time = 2 ** attempt
                    logger.info(
                        "Timeout, retrying in %ds", sleep_time
                    )
                    time.sleep(sleep_time)
                    continue
                raise ZohoAPIError("Request timed out after retries")
        raise ZohoAPIError("Unexpected error in request retry loop")

    def _request(
        self, method: str, path: str, **kwargs: Any
    ) -> dict[str, Any]:
        self._ensure_token()
        url = f"https://{settings.zoho_api_domain}/creator/v2.1/{path}"
        headers = {
            "Authorization": f"Zoho-oauthtoken {self._access_token}",
        }
        resp = self._session.request(
            method, url, headers=headers, timeout=30, **kwargs
        )
        if resp.status_code == 401:
            raise ZohoAuthError("Zoho API returned 401 Unauthorized")
        if resp.status_code == 429:
            raise ZohoRateLimitError("Zoho API rate limit exceeded")
        if 500 <= resp.status_code < 600:
            raise ZohoAPIError(
                f"Zoho API server error: HTTP {resp.status_code}"
            )
        resp.raise_for_status()
        return resp.json()
