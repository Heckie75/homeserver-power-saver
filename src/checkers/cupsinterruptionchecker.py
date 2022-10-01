import logging
import subprocess
from datetime import datetime, timedelta
from sys import platform

from checkers.abstractinterruptionchecker import \
    AbstractInterruptionChecker

LOGGER = logging.getLogger()


class CupsInterruptionChecker(AbstractInterruptionChecker):

    def get_occupation(self, dt_now: datetime) -> timedelta:

        if not platform.startswith("linux"):
            return None

        jobs = [j for j in subprocess.getoutput("lpstat -o").split("\n") if j]
        if jobs:
            for j in jobs:
                LOGGER.debug(j)
            return self.stay_awake

        else:
            return None
