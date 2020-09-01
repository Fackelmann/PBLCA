from typing import Dict

import json
import logging
import requests

FORMAT = "[%(levelname)s - %(asctime)s %(filename)s:%(lineno)s -"\
    "%(funcName)20s()] %(message)s"

logging.basicConfig(format=FORMAT, filename="pblca.log", level=logging.INFO)


class APIAccessException(Exception):
    pass


class APIInitializationException(Exception):
    pass


class PinboardAPI:
    """Pinboard (pinboard.in) client API implementation.

    :param token: Pinboard API token USER:TOKEN
    """
    PINBOARD_API_ENDPOINT = "https://api.pinboard.in/v1"

    def __init__(self, token: str) -> None:
        self.token = token
        try:
            self.get_update()
        except APIAccessException as e:
            raise APIInitializationException("Cannot initialize Pinboard:"
                                             f"{e}")

    def _api_call(self, method: str, **params: str) -> Dict[str, str]:
        params["auth_token"] = self.token
        params["format"] = "json"
        response = requests.get(f"{self.PINBOARD_API_ENDPOINT}{method}",
                                params=params)
        if response.status_code == 200:
            return json.loads(response.content)
        else:
            raise APIAccessException("Cannot access Pinboard"
                                     f"status code ={response.status_code}")

    def get_update(self) -> Dict[str, str]:
        """Return the most recent tima a bookmark was added, updated,
        or deleted.
        :returns: dictionary containing key "update time" """
        return self._api_call("/posts/update")

    def get_recent(self) -> Dict[str, str]:
        return self._api_call("/posts/recent")

    def get_all_posts(self) -> Dict[str, str]:
        return self._api_call("/posts/all")

    def add_post(self, **params: str) -> dict:
        return self._api_call("/posts/add", **params)

    def delete_post(self, **params: str) -> dict:
        return self._api_call("/posts/delete", **params)

    def get_post(self, **params: str) -> dict:
        return self._api_call("/posts/get", **params)
