import requests

class RequestSender:
    def __init__(self, server_url):
        self.server_url = server_url

    def send_request(self, action):
        try:
            payload = {"command": action}
            response = requests.post(self.server_url, json=payload)
            if response.status_code == 200:
                print(f"Request sent successfully: {action}")
            else:
                print(f"Failed to send request: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            print(f"Connection error: {e}")