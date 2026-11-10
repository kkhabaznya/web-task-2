import requests


class APIClient:
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url
        self.headers = {
            "Accept-Language": "ru-RU",
            "Content-Type": "application/json",
        }

    def rest_api_v2_add_client(self, user_agent: str):
        url = f"{self.base_url}/rest/api/v2/add-client"
        return requests.post(
            url, params={"user_agent": user_agent}, headers=self.headers
        ).json()

    def rest_api_v2_collect_client(self, uid: int = None):
        url = f"{self.base_url}/rest/api/v2/collect-client"
        params = {"uid": uid} if uid else {}
        return requests.get(url, params=params, headers=self.headers).json()

    def rest_api_v2_revise_client(self, uid: int, data: dict):
        url = f"{self.base_url}/rest/api/v2/revise-client/{uid}"
        return requests.put(url, json=data, headers=self.headers).json()

    def rest_api_v2_add_message(
        self,
        data: str,
        client_id: int,
        description: str = "",
        tags: str = "",
        stage: str = "",
    ):
        url = f"{self.base_url}/rest/api/v2/add-message"
        params = {
            "data": data,
            "client": client_id,
            "description": description,
            "tags": tags,
            "stage": stage,
        }
        return requests.post(url, params=params, headers=self.headers).json()

    def rest_api_v2_collect_message(self, client_id: int, stage: str = None):
        url = f"{self.base_url}/rest/api/v2/collect-message/{client_id}"
        params = {"stage": stage} if stage else {}
        return requests.get(url, params=params, headers=self.headers).json()

    def rest_api_v2_revise_message(self, uid: int, data: dict):
        url = f"{self.base_url}/rest/api/v2/revise-message/{uid}"
        return requests.put(url, json=data, headers=self.headers).json()

    def rest_api_v2_collect_feedback(self, message_id: int):
        url = f"{self.base_url}/rest/api/v2/collect-feedback/{message_id}"
        return requests.get(url, headers=self.headers).json()

    def rest_api_v2_collect_report(self):
        url = f"{self.base_url}/rest/api/v2/collect-report"
        return requests.get(url, headers=self.headers).json()
