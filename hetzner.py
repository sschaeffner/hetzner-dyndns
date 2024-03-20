import subprocess

import requests
from loguru import logger


class HetznerDns:
    def __init__(self, api_token: str):
        self.api_token = api_token

    def _get(self, path, params=None):
        result = requests.get(
            url=f"https://dns.hetzner.com/api/v1/{path}",
            headers={"Auth-API-Token": self.api_token},
            params={} if params is None else params
        )

        if not result.ok:
            logger.error("HTTP Request failed: {} {}", result, result.text)
            raise Exception("HTTP Request failed")

        return result.json()

    def _post(self, path, json=None):
        result = requests.post(
            url=f"https://dns.hetzner.com/api/v1/{path}",
            headers={"Auth-API-Token": self.api_token},
            json=json
        )

        if not result.ok:
            logger.error("HTTP Request failed: {} {}", result, result.text)
            raise Exception("HTTP Request failed")

        return result.json()

    def _put(self, path, json=None):
        result = requests.put(
            url=f"https://dns.hetzner.com/api/v1/{path}",
            headers={"Auth-API-Token": self.api_token},
            json=json
        )

        if not result.ok:
            logger.error("HTTP Request failed: {} {}", result, result.text)
            raise Exception("HTTP Request failed")

        return result.json()

    def get_zones(self):
        return self._get("zones")["zones"]

    def get_zone_id(self, zone_name: str) -> str | None:
        zones = self.get_zones()
        for zone in zones:
            if zone["name"] == zone_name:
                return zone["id"]
        return None

    def get_records(self, zone_id: str):
        return self._get("records", params={"zone_id": zone_id})[
            "records"]

    def create_record(
            self,
            zone_id: str,
            name: str,
            value: str,
            type_: str = "A",
            ttl: int | None = None
    ):
        body = {
            "name": name,
            "type": type_,
            "value": value,
            "zone_id": zone_id
        }
        if ttl:
            body["ttl"] = ttl

        result = self._post("records", json=body)
        logger.debug(f"create record result: {result}")

    def update_record(
            self,
            record_id: str,
            zone_id: str,
            name: str,
            value: str,
            type_: str = "A",
            ttl: int | None = None
    ):
        body = {
            "name": name,
            "type": type_,
            "value": value,
            "zone_id": zone_id
        }
        if ttl:
            body["ttl"] = ttl

        result = self._put(f"records/{record_id}", json=body)
        logger.debug(f"update record result: {result}")


class HetznerIp:
    url = "https://ip.hetzner.com"

    def get_ip4(self):
        process = subprocess.run(["curl", "-4", self.url], capture_output=True)
        process.check_returncode()
        return process.stdout.decode("utf-8").strip()

    def get_ip6(self):
        process = subprocess.run(["curl", "-6", self.url], capture_output=True)
        process.check_returncode()
        return process.stdout.decode("utf-8").strip()
