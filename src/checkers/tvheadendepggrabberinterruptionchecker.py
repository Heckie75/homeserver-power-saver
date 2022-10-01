import json
import logging
from datetime import datetime, timedelta

from checkers.abstractinterruptionchecker import AbstractInterruptionChecker

try:
    import croniter
except ImportError:
    pass

LOGGER = logging.getLogger()


class TvHeadendEpgGrabberInterruptionChecker(AbstractInterruptionChecker):

    def __init__(self, setting) -> None:
        super().__init__(setting)

    def _read_epg_config(self, path: str) -> 'dict':

        with open(path, encoding="iso-8859-1", mode="r") as f:
            return json.loads("\n".join([l for l in f.readlines()]))

    def get_upcoming_event(self, dt_now: datetime) -> datetime:

        def _parse_cron(s: str) -> 'list[croniter.croniter]':

            _iters = list()
            for l in s.split("\n"):
                if not l.startswith("#"):
                    try:
                        _iters.append(croniter.croniter(l, dt_now))
                    except:
                        pass

            return _iters

        conf = self._read_epg_config(self.setting["epg_config_path"])

        cron_iters = list()
        if [m for m in conf["modules"] if conf["modules"][m]["type"] == "Over-the-air" and conf["modules"][m]["enabled"]]:
            cron_iters.extend(_parse_cron(conf["ota_cron"]))

        if [m for m in conf["modules"] if conf["modules"][m]["type"] == "Internal" and conf["modules"][m]["enabled"]]:
            cron_iters.extend(_parse_cron(conf["cron"]))

        closest_event = None
        for ci in cron_iters:
            dt_schedule = ci.get_next(datetime)
            closest_event = dt_schedule if not closest_event or (
                dt_schedule and dt_schedule < closest_event) else closest_event

        return closest_event
