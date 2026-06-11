import logging
from datetime import datetime, timedelta

from checkers.abstractinterruptionchecker import AbstractInterruptionChecker
from utils.kodijsonrpcclient import KodiJsonRpcClient

LOGGER = logging.getLogger()


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
