import json
import logging
import os
import time
from datetime import datetime, timedelta

from checkers.abstractinterruptionchecker import AbstractInterruptionChecker
from utils.kodijsonrpcclient import KodiJsonRpcClient

LOGGER = logging.getLogger()


class KodiWizInterruptionChecker(AbstractInterruptionChecker):

    def __init__(self, setting) -> None:

        super().__init__(setting)

        self._wiz_running_programs_file = setting.get("path")

        if setting.get("preaction", False) or setting.get("postaction", False):
            self._kodiJsonRpcClient = KodiJsonRpcClient(
                setting["host"], setting["port"], setting["user"], setting["password"])
        else:
            self._kodiJsonRpcClient = None

        self._running_programs = []

    def _load_wiz_running_programs_file(self) -> list[dict]:

        _wiz_running_programs_file = os.path.expanduser(
            self._wiz_running_programs_file)
        if not os.path.isfile(_wiz_running_programs_file):
            return []

        try:
            with open(_wiz_running_programs_file, "r") as f:
                return json.loads("\n".join(f.readlines()))

        except:
            LOGGER.error("Failed to read running programs file %s" %
                         _wiz_running_programs_file, exc_info=True)
            return []

    def get_occupation(self, dt_now: datetime) -> timedelta:

        running_programs = self._load_wiz_running_programs_file()
        max_timestamp = max([0] + [program.get("start_time", 0) + program.get("duration", 0)
                                   for program in running_programs])

        max_dt = datetime.fromtimestamp(max_timestamp)
        if max_dt > dt_now:
            return min(max_dt - dt_now, self.stay_awake)

        return None

    def perform_pre_action(self, dt_wakeup):

        self._running_programs = self._load_wiz_running_programs_file()
        for program in self._running_programs:
            params = {
                "ip_addresses": ";".join(program["ip_addresses"]),
                "program": "halt"
            }
            self._kodiJsonRpcClient.execute_addon("script.wiz", params)
            time.sleep(1)

    def perform_post_action(self):

        for program in self._running_programs:
            params = {
                "ip_addresses": ";".join(program["ip_addresses"]),
                "program": program["programID"],
                "duration":  program["duration"],
                "dimming":  program["dimming"],
                "offset": int(time.time() - program["start_time"])
            }
            self._kodiJsonRpcClient.execute_addon("script.wiz", params)

        self._running_programs = []
