from unittest.mock import MagicMock, patch

import pytest
import requests

from services.zoho_client import (
    ZohoClient,
    ZohoAuthError,
    ZohoRateLimitError,
    ZohoAPIError,
)


@pytest.fixture
def client():
    c = ZohoClient()
    c._access_token = "test_token"
    c._token_expiry = __import__("time").time() + 99999
    return c


def make_json_response(status_code, json_data, headers=None):
    resp = MagicMock(spec=requests.Response)
    resp.status_code = status_code
    resp.json.return_value = json_data
    resp.headers = headers or {}
    return resp


class TestZohoClient:
    def test_successful_get_records(self, client):
        page1 = make_json_response(
            200, {"data": [{"id": "1"}], "record_cursor": "cursor2"}
        )
        page2 = make_json_response(200, {"data": [{"id": "2"}]})
        with patch.object(client._session, "request") as mock_req:
            mock_req.side_effect = [page1, page2]

            results = client.get_records("Projects")

            assert len(results) == 2
            assert results[0]["id"] == "1"
            assert results[1]["id"] == "2"
            assert mock_req.call_count == 2

    def test_token_refresh_on_401(self, client):
        unauth = make_json_response(401, {})
        ok = make_json_response(200, {"data": [{"id": "1"}]})
        refresh_ok = make_json_response(
            200,
            {"access_token": "new_token", "expires_in_sec": 3600},
        )
        with (
            patch.object(client._session, "request") as mock_req,
            patch.object(client._session, "post") as mock_post,
        ):
            mock_req.side_effect = [unauth, ok]
            mock_post.return_value = refresh_ok
            client._access_token = "expired_token"
            client._token_expiry = 0

            result = client.get_records("Projects")

            assert result == [{"id": "1"}]
            assert mock_post.called

    def test_retry_on_429(self, client):
        too_many = make_json_response(429, {})
        ok = make_json_response(200, {"data": [{"id": "1"}]})
        with patch.object(client._session, "request") as mock_req:
            mock_req.side_effect = [too_many, too_many, too_many, ok]

            results = client.get_records("Projects")

            assert results == [{"id": "1"}]
            assert mock_req.call_count == 4

    def test_zoho_rate_limit_error(self, client):
        too_many = make_json_response(429, {})
        with patch.object(client._session, "request") as mock_req:
            mock_req.side_effect = [too_many, too_many, too_many, too_many]

            with pytest.raises(ZohoRateLimitError):
                client.get_records("Projects")

    def test_zoho_api_error(self, client):
        bad_gateway = make_json_response(502, {})
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = bad_gateway

            with pytest.raises(ZohoAPIError):
                client.get_records("Projects")

    def test_owner_app_in_url(self, client):
        from config import settings

        settings.zoho_owner = "testowner"
        settings.zoho_app_name = "testapp"
        ok = make_json_response(200, {"data": []})
        with patch.object(client._session, "request") as mock_req:
            mock_req.return_value = ok

            client.get_records("Expenses")

            args, kwargs = mock_req.call_args
            call_url = args[1] if len(args) > 1 else ""
            assert "testowner" in call_url
            assert "testapp" in call_url
