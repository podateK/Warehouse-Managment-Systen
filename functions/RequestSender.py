import requests
import json
from urllib.parse import urlparse
from functions.ConfigManager import ConfigManager

class RequestSender:
    _ACTION_MAP = {
        "FORWARD": "forward",
        "STOP": "stop",
        "MOVE_LEFT": "left",
        "MOVE_RIGHT": "right",
        "BACK": "back",
        "ACTION_LIFT": "lift",
        "ACTION_LOWER": "lower",
    }

    def __init__(self, server_url=None):
        if server_url is None:
            server_url = ConfigManager.get_robot_command_url()
        self.server_url = server_url

    def _normalize_action(self, action):
        action_text = str(action).strip()
        mapped = self._ACTION_MAP.get(action_text.upper())
        if mapped:
            return mapped
        return action_text.lower()

    def build_send_request_url(self, action):
        action_value = self._normalize_action(action)
        parsed_url = urlparse(self.server_url)
        scheme = parsed_url.scheme or "http"
        netloc = parsed_url.netloc or parsed_url.path
        send_url = f"{scheme}://{netloc}/send"
        params = {"data": action_value}
        return requests.Request("GET", send_url, params=params).prepare().url

    def send_request(self, action):
        """
        Send request to robot server
        Returns: (success: bool, message: str)
        """
        action_value = self._normalize_action(action)
        prepared_url = self.build_send_request_url(action)
        parsed_url = urlparse(prepared_url)
        send_url = f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path}"
        params = {"data": action_value}

        print(f"📤 REQUEST -> GET {prepared_url}", flush=True)
        print(f"📤 CURL -> curl \"{prepared_url}\"", flush=True)
        try:
            timeout = ConfigManager.get_robot_timeout()
            response = requests.get(send_url, params=params, timeout=timeout)
            response_body = response.text if response.text is not None else ""
            normalized_body = response_body.strip()

            if response.status_code == 200:
                if not normalized_body:
                    normalized_body = "Online"
                print(f"✓ RESPONSE <- {response.status_code} | body={normalized_body}", flush=True)
                return True, f"request={response.url} | response={normalized_body}"

            print(f"✗ RESPONSE <- {response.status_code} | body={response_body}", flush=True)
            return False, f"request={response.url} | HTTP {response.status_code}: {response_body}"
        except requests.exceptions.ConnectionError as e:
            print(f"✗ Connection error for action={action_value}: {e}", flush=True)
            return False, f"request={send_url}?data={action_value} | Robot jest wyłączony lub niedostępny"
        except requests.exceptions.Timeout:
            print(f"✗ Request timeout for action={action_value}", flush=True)
            return False, f"request={send_url}?data={action_value} | Timeout - robot nie odpowiada"
        except requests.exceptions.RequestException as e:
            print(f"✗ Request error for action={action_value}: {e}", flush=True)
            return False, f"request={send_url}?data={action_value} | Błąd: {str(e)}"

    def send_json(self, payload):
        """
        Backward-compatible method name: sends payload with GET query params.
        Returns: (success: bool, message: str)
        """
        payload_json = json.dumps(payload, ensure_ascii=False)
        parsed_url = urlparse(self.server_url)
        scheme = parsed_url.scheme or "http"
        netloc = parsed_url.netloc or parsed_url.path
        send_url = f"{scheme}://{netloc}/send"

        params = {}
        if isinstance(payload, dict):
            if "command" in payload:
                params["data"] = self._normalize_action(payload.get("command"))

            for key, value in payload.items():
                if key == "command":
                    continue
                if isinstance(value, (dict, list)):
                    params[key] = json.dumps(value, ensure_ascii=False)
                elif isinstance(value, str):
                    params[key] = value.lower()
                else:
                    params[key] = str(value)
        else:
            params["data"] = str(payload).lower()

        prepared_url = requests.Request("GET", send_url, params=params).prepare().url
        print(f"📤 REQUEST -> GET {prepared_url}", flush=True)
        print(f"📤 CURL -> curl \"{prepared_url}\"", flush=True)
        try:
            timeout = ConfigManager.get_robot_timeout()
            response = requests.get(send_url, params=params, timeout=timeout)
            response_body = response.text if response.text is not None else ""
            normalized_body = response_body.strip()
            if response.status_code == 200:
                if not normalized_body:
                    normalized_body = "Online"
                print(f"✓ RESPONSE <- {response.status_code} | body={normalized_body}", flush=True)
                return True, f"request={response.url} | response={normalized_body}"
            else:
                print(f"✗ RESPONSE <- {response.status_code} | body={response_body}", flush=True)
                return False, f"request={response.url} | HTTP {response.status_code}: {response_body}"
        except requests.exceptions.ConnectionError as e:
            print(f"✗ Connection error for body={payload_json}: {e}", flush=True)
            return False, f"request={prepared_url} | Robot jest wyłączony lub niedostępny"
        except requests.exceptions.Timeout:
            print(f"✗ Request timeout for body={payload_json}", flush=True)
            return False, f"request={prepared_url} | Timeout - robot nie odpowiada"
        except requests.exceptions.RequestException as e:
            print(f"✗ Request error for body={payload_json}: {e}", flush=True)
            return False, f"request={prepared_url} | Błąd: {str(e)}"
