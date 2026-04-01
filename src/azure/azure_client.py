import base64
import requests
from src.config import Settings


class AzureDevOpsClient:
    def __init__(self):
        if not Settings.AZURE_PAT:
            raise ValueError("AZURE_PAT is missing in .env")

        token = f":{Settings.AZURE_PAT}".encode("utf-8")
        encoded_token = base64.b64encode(token).decode("utf-8")

        self.headers = {
            "Authorization": f"Basic {encoded_token}",
            "Content-Type": "application/json"
        }

    def get_work_item(self, work_item_id: int) -> dict:
        url = (
            f"https://dev.azure.com/{Settings.AZURE_ORG}/"
            f"{Settings.AZURE_PROJECT}/_apis/wit/workitems/{work_item_id}"
            f"?api-version={Settings.AZURE_API_VERSION}"
        )

        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        return response.json()

    def get_work_item_with_details(self, work_item_id: int) -> dict:
        url = (
            f"https://dev.azure.com/{Settings.AZURE_ORG}/"
            f"{Settings.AZURE_PROJECT}/_apis/wit/workitems/{work_item_id}"
            f"?$expand=relations&api-version={Settings.AZURE_API_VERSION}"
        )

        response = requests.get(url, headers=self.headers, timeout=30)
        response.raise_for_status()
        data = response.json()
        data["comments"] = []
        data["attachments"] = []
        return data

    def build_work_item_url(self, work_item_id: int) -> str:
        return (
            f"https://dev.azure.com/{Settings.AZURE_ORG}/"
            f"{Settings.AZURE_PROJECT}/_workitems/edit/{work_item_id}"
        )
