import requests

class RequestSender:
    def __init__(self, server_url):
        self.server_url = server_url

    def send_request(self, action):
        try:
            payload = {"command": action}
            response = requests.post(self.server_url, json=payload, timeout=5)
            if response.status_code == 200:
                print(f"✓ Request sent successfully: {action} -> {self.server_url}")
            else:
                print(f"✗ Failed to send request: {response.status_code}, {response.text}")
        except requests.exceptions.ConnectionError as e:
            print(f"✗ Connection error (server not running?): {e}")
        except requests.exceptions.Timeout:
            print(f"✗ Request timeout: {action}")
        except requests.exceptions.RequestException as e:
            print(f"✗ Request error: {e}")