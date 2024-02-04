import json as json_module
import os
import time
from typing import Optional, Any

DEFAULT_SERVER_URL = "https://table.nju.edu.cn"

try:
    from numpy import random

    USE_NUMPY = True
except ImportError:
    import random

    USE_NUMPY = False

try:
    import requests

    USE_REQUESTS = True
except Exception as e:
    import urllib

    USE_REQUESTS = False


class ResponseMock(object):
    def __init__(self, text: str, status_code: int) -> None:
        self.text = text
        self.status_code = status_code


class BaseMock(object):
    def __init__(self, api_token: str, server_url: str) -> None:
        self.token = api_token
        self.server_url = self._parse_server_url(server_url)

        self.timeout = 30

        self.headers = None
        self._row_server_url = None

    @staticmethod
    def _parse_server_url(server_url: str) -> str:
        return server_url.rstrip("/")

    @staticmethod
    def _parse_headers(token: str) -> str:
        return {
            "Authorization": "Token " + token,
            "Content-Type": "application/json",
        }

    @staticmethod
    def _parse_response(response: Any) -> dict:
        if response.status_code >= 400:
            raise ConnectionError(response.status_code, response.text)
        else:
            try:
                return json_module.loads(response.text)
            except:
                return {}

    def _request_get(
        self, url: str, headers: Optional[dict] = None, params: Optional[dict] = None
    ) -> Any:
        if USE_REQUESTS:
            r = requests.get(url, params=params, headers=headers, timeout=self.timeout)
            return r
        else:
            if params:
                query = urllib.parse.urlencode(params)
                url = url.rstrip("/") + "?" + query
            request = urllib.request.Request(url)
            if headers:
                for k, v in headers.items():
                    request.add_header(k, v)
            with urllib.request.urlopen(request) as response:
                text = response.read().decode("utf-8")
                status_code = response.status
                return ResponseMock(text, status_code)

    def _request_put(
        self, url: str, json: Optional[dict] = None, headers: Optional[dict] = None
    ) -> Any:
        if USE_REQUESTS:
            r = requests.put(url, json=json, headers=headers, timeout=self.timeout)
            return r
        else:
            request = urllib.request.Request(url, method="PUT")

            data = None
            if json:
                data = json_module.dumps(json).encode("utf-8")
                request.add_header("Content-Type", "application/json; charset=utf-8")
                request.add_header("Content-Length", len(data))

            if headers:
                for k, v in headers.items():
                    request.add_header(k, v)

            with urllib.request.urlopen(request, data=data) as response:
                text = response.read().decode("utf-8")
                status_code = response.status
                return ResponseMock(text, status_code)

    def auth(self) -> None:
        url = self.server_url + "/api/v2.1/dtable/app-access-token/"
        headers = self._parse_headers(self.token)

        response = self._request_get(url, headers=headers)
        data = self._parse_response(response)

        self.jwt_token = data.get("access_token")
        self.headers = self._parse_headers(self.jwt_token)

        dtable_server_url = self._parse_server_url(data.get("dtable_server"))
        dtable_uuid = data.get("dtable_uuid")

        self._row_server_url = (
            dtable_server_url + "/api/v1/dtables/" + dtable_uuid + "/rows/"
        )

    def list_rows(self, table_name: str, limit: Optional[int] = None) -> list:
        params = {"table_name": table_name}

        if limit:
            params["limit"] = limit

        response = self._request_get(
            self._row_server_url, params=params, headers=self.headers
        )

        return self._parse_response(response).get("rows")

    def update_row(self, table_name: str, row_id: str, row_data: dict) -> dict:
        json_data = {
            "table_name": table_name,
            "row_id": row_id,
            "row": row_data,
        }

        response = self._request_put(
            self._row_server_url, json=json_data, headers=self.headers
        )

        return self._parse_response(response)


class Eurus(object):
    def __init__(self) -> None:
        self._rng = None
        self.server_url = DEFAULT_SERVER_URL
        self.api_token = os.environ.get("TABLE_API_TOKEN", None)

    def configure(
        self,
        api_token: Optional[str] = None,
        server_url: Optional[str] = None,
    ) -> None:
        if server_url:
            self.server_url = server_url
        if api_token:
            self.api_token = api_token

    def _unsafe_send(
        self, message: str, group: Optional[str] = None, api_token: Optional[str] = None
    ) -> dict:
        random_seed = int(time.time() * 1000) % 100

        api_token = api_token if api_token else self.api_token

        if api_token is None:
            raise AssertionError("Empty API_TOKEN!")

        base = BaseMock(api_token, self.server_url)
        base.auth()

        if USE_NUMPY:
            self._rng = random.RandomState(random_seed)
        else:
            # save initial system rng state, so random state will not break after sending message
            self._initial_random_state = random.get_state()
            random.seed(random_seed)
            self._rng = random

        # ================ Danger Zone Starts ================
        rows = base.list_rows("Buffer")
        rows = [row for row in rows if row.get("Content") is None]

        target_row = self._rng.choice(rows)

        r = base.update_row(
            "Buffer", target_row["_id"], {"Name": group, "Content": message}
        )
        # ================ Danger Zone Ends ================

        return r

    def send(
        self, message: str, group: Optional[str] = None, api_token: Optional[str] = None
    ) -> dict:
        self._initial_random_state = None
        try:
            return self._unsafe_send(message=message, group=group, api_token=api_token)
        except Exception as e:
            return {"success": False, "error_message": repr(e)}
        finally:
            if self._initial_random_state is not None:
                random.set_state(self._initial_random_state)


eurus = Eurus()

if __name__ == "__main__":
    TABLE_API_TOKEN = "*********************"

    eurus.configure(TABLE_API_TOKEN)
    result = eurus.send("**Title**\Hello\nWorld")

    print(result)
