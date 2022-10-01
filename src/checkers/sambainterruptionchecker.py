import logging
import re
import subprocess
from datetime import datetime, timedelta
from sys import platform

from checkers.abstractinterruptionchecker import \
    AbstractInterruptionChecker

LOGGER = logging.getLogger()


class SambaInterruptionChecker(AbstractInterruptionChecker):

    _SMBSTATUS_LOCKS_PATTERN = r"^(\d+) +(\d+) +([^ ]+) +([^ ]+) +([^ ]+) +([^ ]+) +(.*) +(\w+ \w+ \d+ \d{2}:\d{2}:\d{2} \d{4})$"

    def get_occupation(self, dt_now: datetime) -> timedelta:

        if not platform.startswith("linux"):
            return None

        locks = list()

        lines = subprocess.getoutput("smbstatus --locks").split("\n")
        for l in lines:

            m = re.match(self._SMBSTATUS_LOCKS_PATTERN, l)
            if not m or m.groups()[6].strip().endswith(" ."):
                continue

            else:
                locks.append((m.groups()[1], m.groups()[6].strip()))

        if locks:
            for l in locks:
                LOGGER.debug("user=%s, lock=%s" % l)
            return self.stay_awake

        else:
            return None
