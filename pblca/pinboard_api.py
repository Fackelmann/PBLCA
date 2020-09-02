"""Basic Pinboard API"""
import json
import requests


class APIAccessException(Exception):
    """Custom exception. Error accessing Pinboard API"""


class APIInitializationException(Exception):
    """Custom Exception. Cannot initialize instance and connect to Pinboard"""


class PinboardAPI:
    """Pinboard (pinboard.in) client API implementation.

    :param token: Pinboard API token USER:TOKEN
    """
    PINBOARD_API_ENDPOINT = "https://api.pinboard.in/v1"

    def __init__(self, token: str) -> None:
        self.token = token
        try:
            self.get_update()
        except APIAccessException as exception:
            raise APIInitializationException("Cannot initialize Pinboard:"
                                             f"{exception}")

    def _api_call(self, method: str, **params: str) -> dict:
        params["auth_token"] = self.token
        params["format"] = "json"
        response = requests.get(f"{self.PINBOARD_API_ENDPOINT}{method}",
                                params=params)
        if response.status_code == 200:
            return json.loads(response.content)
        raise APIAccessException("Cannot access Pinboard"
                                 f"status code ={response.status_code}")

    def get_update(self) -> dict:
        """Returns the most recent tima a bookmark was added, updated,
        or deleted.
        :returns: dictionary containing key "update time" """
        return self._api_call("/posts/update")

    def get_recent_posts(self) -> dict:
        """Returns the most recent time a bookmark was added, updated,
        or deleted."""
        return self._api_call("/posts/recent")

    def get_all_posts(self) -> dict:
        """Returns all bookmarks in the user's account."""
        return self._api_call("/posts/all")

    def add_post(self, **params: str) -> dict:
        """Adds a bookmark."""
        return self._api_call("/posts/add", **params)

    def delete_post(self, **params: str) -> dict:
        """Deletes a bookmark."""
        return self._api_call("/posts/delete", **params)

    def get_post(self, **params: str) -> dict:
        """Returns one or more posts on a single day matching the arguments.
        If no date or url is given, date of most recentbookmark will be
        used."""
        return self._api_call("/posts/get", **params)
