import logging
import re
import subprocess
from datetime import datetime, timedelta
from sys import platform

from checkers.abstractinterruptionchecker import \
    AbstractInterruptionChecker

LOGGER = logging.getLogger()


class LoadInterruptionChecker(AbstractInterruptionChecker):

    UPTIME_PATTERN = r"^.*load average: ([\d\.]+), ([\d\.]+), ([\d\.]+)$"

    def get_occupation(self, dt_now: datetime) -> timedelta:

        if not platform.startswith("linux"):
            return None

        out = subprocess.getoutput("LANG=en uptime")
        m = re.match(self.UPTIME_PATTERN, out)
        if m:
            load = float(m.groups()[0])
            if load >= self.setting["threshold"]:
                LOGGER.debug("Current load %.2f is higher than threshold %.2f." % (load, self.setting["threshold"]))

                return self.stay_awake

        return None
