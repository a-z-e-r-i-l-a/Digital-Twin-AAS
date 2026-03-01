import requests
import base64
import json
from pathlib import Path
import sys, os
# from basyx.aas import model
# from basyx.aas.adapter import aasx


def base64url_encode(data: str) -> str:
    """Base64url-encode a string (no padding), as required by BaSyx AAS V3 API."""
    return base64.urlsafe_b64encode(data.encode("utf-8")).decode("utf-8").rstrip("=")


# def save_dict_to_json(data: dict, filepath: Path) -> None:
#     with open(filepath, 'w', encoding='utf-8') as f:
#         json.dump(data, f, ensure_ascii=False, indent=4)


# def get_aas_id_from_aasx(filepath: Path) -> str:
#         new_object_store: model.DictObjectStore[model.Identifiable] = (
#             model.DictObjectStore()
#         )
#         new_file_store = aasx.DictSupplementaryFileContainer()
#         with aasx.AASXReader(filepath) as reader:
#             reader.read_into(object_store=new_object_store, file_store=new_file_store)
#         aas_id = list(new_object_store)[0].id
#         return aas_id


class AASInterface(object):
    def __init__(self, asset_name='f-x-template-ohne-mes-001',
                       submodel_name='Factory-X ManufacturingProcess-001',
                       base_url=None,
                       client_id=None,
                       client_secret=None,
                       aas_type='AAS (BaSyx)',
                ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.asset_name = asset_name
        self.submodel_name = submodel_name
        self.asset_id = base64url_encode(self.asset_name)
        self.submodel_id = base64url_encode(self.submodel_name)
        self.aas_type = aas_type

        if base_url is None:
            if self.aas_type == 'AAS (BaSyx)':
                base_url = "http://localhost:8081"
            else:
                base_url = "https://test.assetfox.apps.siemens.cloud/api/aas/v3"

        if self.aas_type == 'AAS (BaSyx)':
            self.base_url = base_url.rstrip("/")
        else:
            self.aas_type = 'AAS (AssetFox)'
            self.base_url = f"{base_url}/shells/{self.asset_id}"

    def _headers(self) -> dict:
        """Build request headers, including auth only for AssetFox."""
        headers = {"Content-Type": "application/json"}
        if self.aas_type == 'AAS (AssetFox)':
            headers["Authorization"] = f"Bearer {self.fetch_assetfox_token()}"
        return headers

    def fetch_assetfox_token(self) -> str:
        if self.aas_type == 'AAS (BaSyx)':
            return None
        token_url = "https://test.assetfox.apps.siemens.cloud/auth/realms/assetfox/protocol/openid-connect/token"

        self.client_id = "F1DS944RHY"
        self.client_secret = "s]j8Qfy!b@3Y27!"

        response = requests.post(
            token_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=10,
        )
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("access_token")

    def find_shells(self):
        if self.aas_type == 'AAS (BaSyx)':
            url = f"{self.base_url}/shells"
        else:
            url = f"{self.base_url}/lookup/shells"
        response = requests.get(url, headers=self._headers(), timeout=10)
        response.raise_for_status()
        return response.json()

    def get_shell_asset(self, shell_name):
        self.asset_id = base64url_encode(shell_name)
        response = requests.get(
            f"{self.base_url}/shells/{self.asset_id}",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def get_asset_submodel(self):
        response = requests.get(
            f"{self.base_url}/submodels/{self.submodel_id}",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def get_asset_submodel_element(self, element_id):
        response = requests.get(
            f"{self.base_url}/submodels/{self.submodel_id}/submodel-elements/{element_id}",
            headers=self._headers(),
            timeout=10,
        )
        response.raise_for_status()
        return response.json()

    def get_property(self, element_id, idShort):
        asset = self.get_asset_submodel_element(element_id)
        value = next(item["value"] for item in asset["value"] if item.get("idShort") == idShort)
        return value

    def get_smc_prop(self, element_id, idShort):
        asset = self.get_asset_submodel_element(element_id)
        value = next(item["value"] for item in asset["value"] if item.get("idShort") == idShort)
        return value

    def get_smc_ref(self, element_id, idShort):
        asset = self.get_asset_submodel_element(element_id)
        return next(item for item in asset["value"] if item.get("idShort") == idShort)["value"]['keys'][0]['value']

    def set_smc_prop(self, element_id, idShort, value):
        asset = self.get_asset_submodel_element(element_id)
        next(item for item in asset["value"] if item.get("idShort") == idShort)["value"] = value
        self.send_request(self.asset_id, self.submodel_id, element_id, body_msg=asset)

    def set_property(self, element_id, idShort, value):
        asset = self.get_asset_submodel_element(element_id)
        next(item for item in asset["value"] if item.get("idShort") == idShort)["value"] = value
        self.send_request(self.asset_id, self.submodel_id, element_id, body_msg=asset)

    def set_reference(self, element_id, idShort, value):
        asset = self.get_asset_submodel_element(element_id)
        next(i for i in asset["value"] if i["idShort"] == idShort)["value"]["keys"][0]["value"] = value
        self.send_request(self.asset_id, self.submodel_id, element_id, body_msg=asset)

    def send_request(self, asset_id, submodel_id, element_id, body_msg):
        response = requests.put(
            f"{self.base_url}/submodels/{submodel_id}/submodel-elements/{element_id}",
            headers=self._headers(),
            json=body_msg,
            timeout=10,
        )
        response.raise_for_status()
        return response.json()





