import json
from typing import Final
from tools.api_manager import APIManager

IPROXY_API_KEY: Final = "PRXC4MLYWSTDEBCXZ27GHZT"


async def check_me():
    url = "https://api.iproxy.online/v1/me"
    headers = {
        "Authorization": IPROXY_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = await APIManager.make_request("get", url, headers=headers)
    return response


async def get_connections():
    url = "https://api.iproxy.online/v1/connections"
    headers = {
        "Authorization": IPROXY_API_KEY,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    response = await APIManager.make_request("get", url, headers=headers)
    return response


async def ip_changer(connection_id, status=True, interval=15):
    url = f"https://api.iproxy.online/v1/connections/{connection_id}"
    headers = {
        "Authorization": IPROXY_API_KEY,
        "Content-Type": "application/merge-patch+json",
        "Accept": "application/merge-patch+json",
    }
    data = {
        "ipChangeEnabled": status,
        "ipChangeMinutesInterval": interval
    }

    response = await APIManager.make_request("patch", url, headers=headers, data=json.dumps(data))
    return response


async def get_change_ip_url(pname):
    data = await get_connections()
    if data is not None:
        for item in data['result']:
            if item['name'] == pname:
                return item['changeIpUrl']

    return None