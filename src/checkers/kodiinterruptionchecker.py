import json
import logging
from datetime import datetime, timedelta

import requests

from checkers.abstractinterruptionchecker import \
    AbstractInterruptionChecker

LOGGER = logging.getLogger()


class KodiJsonRpcClient():

    def __init__(self, host, port, user, password) -> None:

        self._host = host
        self._port = port
        self._user = user
        self._password = password

    def _request(self, payload) -> 'dict':

        try:
            response = requests.request("POST", "http://%s:%i/jsonrpc" % (
                self._host, self._port), auth=(self._user, self._password) if self._user and self._password else None, data=json.dumps(payload))

            if response.ok:
                LOGGER.debug(response.text)
                return json.loads(response.text)

            else:
                LOGGER.error("Kodi has responded with HTTP status code %i" % response.status_code)
                return None
        except:
            LOGGER.error("Unexpected error", exc_info=True)
            return None

    def get_active_players(self) -> 'list[dict]':

        payload = [
            {"jsonrpc": "2.0", "method": "Player.GetActivePlayers", "params": {}, "id": 1}]
        response = self._request(payload=payload)
        if response:
            LOGGER.debug(json.dumps(response, indent=2))
            return response[0]["result"]
        else:
            return []

    def stop_player(self, playerid: int) -> None:

        payload = [{"jsonrpc": "2.0", "method": "Player.Stop",
                    "params": [playerid], "id":1}]
        self._request(payload=payload)


class KodiInterruptionChecker(AbstractInterruptionChecker):

    def __init__(self, setting) -> None:

        super().__init__(setting)

        self._kodiJsonRpcClient = KodiJsonRpcClient(
            setting["host"], setting["port"], setting["user"], setting["password"])

    def get_occupation(self, dt_now: datetime) -> timedelta:

        return self.stay_awake if self._kodiJsonRpcClient.get_active_players() else None

    def perform_pre_action(self, dt_wakeup: datetime) -> None:

        for p in self._kodiJsonRpcClient.get_active_players():
            LOGGER.info("Stopping %s" % p["type"])
            self._kodiJsonRpcClient.stop_player(p["playerid"])
