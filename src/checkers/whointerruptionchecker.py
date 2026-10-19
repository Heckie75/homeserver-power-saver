import logging
import re
import subprocess
from datetime import datetime, timedelta
from sys import platform

from checkers.abstractinterruptionchecker import \
    AbstractInterruptionChecker

LOGGER = logging.getLogger()


class WhoInterruptionChecker(AbstractInterruptionChecker):

    def _who(self) -> list[str]:

        LOGGER.debug("query who's logged in")

        ignore = self.setting.get("ignore")
        ignore_pattern = re.compile(ignore) if ignore is not None else None

        lines = subprocess.getoutput("w -h").splitlines()
        active_lines = []
        for line in lines:
            LOGGER.debug(line)
            if ignore_pattern is None or not ignore_pattern.search(line):
                active_lines.append(line)

        return active_lines

    def get_occupation(self, dt_now: datetime) -> timedelta:

        if not platform.startswith("linux"):
            return None

        if self._who():
            return self.stay_awake
        return None
