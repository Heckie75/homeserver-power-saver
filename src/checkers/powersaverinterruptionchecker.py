import logging
import subprocess
import time
from datetime import datetime, timedelta

from checkers.abstractinterruptionchecker import \
    AbstractInterruptionChecker
from utils.periods import Periods
from utils.datetimeutils import format_datetime

LOGGER = logging.getLogger()


class PowerSaverInterruptionChecker(AbstractInterruptionChecker):

    def __init__(self, setting) -> None:
        super().__init__(setting)

        self._preactions = setting["preactions"] if "preactions" in setting else list(
        )
        self._postactions = setting["postactions"] if "postactions" in setting else list(
        )

        self._periods = Periods()
        self._periods.append_from_settings(setting["uptimes"])
        LOGGER.info("Effective uptimes:\n%s" % str(self._periods))

    def get_occupation(self, dt_now: datetime) -> timedelta:

        running, period = self._periods.get_next_period(dt_now)
        return period.end - timedelta(seconds=dt_now.timestamp()) if running else None

    def get_upcoming_event(self, dt_now: datetime) -> datetime:

        running, period = self._periods.get_next_period(dt_now)
        return datetime.fromtimestamp(period.start.total_seconds()) if period else None

    def perform_pre_action(self, dt_wakeup: datetime) -> None:

        s_wakeup = format_datetime(dt_wakeup)
        for c in self._preactions:
            LOGGER.info("Perform pre-action %s" % " ".join(c))
            self._perform_subprocess([s.replace("$[wakeup]", s_wakeup) for s in c])
            time.sleep(1)

    def perform_post_action(self) -> None:

        for c in self._postactions:
            time.sleep(1)
            LOGGER.info("Perform post-action %s" % " ".join(c))
            self._perform_subprocess(c)

    def _perform_subprocess(self, args: 'list[str]') -> None:

        with subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE) as p:

            out, err = p.communicate()
            if out:
                LOGGER.info(out.decode("utf-8"))

            if err:
                LOGGER.error(err.decode("utf-8"))
