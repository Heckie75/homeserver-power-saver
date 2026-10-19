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

        try:
            active_players = self._kodiJsonRpcClient.get_active_players()
        except RuntimeError as error:
            LOGGER.warning(
                "%s: Failed to check Kodi activity; assuming Kodi is not occupied: %s",
                self.__class__.__name__, " ".join(str(error).splitlines()))
            return None

        return self.stay_awake if active_players else None

    def perform_pre_action(self, dt_wakeup: datetime) -> None:

        try:
            active_players = self._kodiJsonRpcClient.get_active_players()
        except RuntimeError as error:
            LOGGER.warning(
                "%s: Failed to check Kodi activity; assuming no players to stop: %s",
                self.__class__.__name__, " ".join(str(error).splitlines()))
            return

        for p in active_players:
            LOGGER.info("Stopping %s" % p["type"])
            try:
                self._kodiJsonRpcClient.stop_player(p["playerid"])
            except RuntimeError as error:
                LOGGER.warning(
                    "%s: Failed to stop Kodi %s player %s: %s",
                    self.__class__.__name__, p["type"], p["playerid"],
                    " ".join(str(error).splitlines()))
