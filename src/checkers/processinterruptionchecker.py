import logging
import subprocess
from datetime import datetime, timedelta
from sys import platform

from checkers.abstractinterruptionchecker import \
    AbstractInterruptionChecker

LOGGER = logging.getLogger()


class ProcessInterruptionChecker(AbstractInterruptionChecker):

    def get_occupation(self, dt_now: datetime) -> timedelta:

        if not platform.startswith("linux"):
            return None

        processes = subprocess.getoutput("ps -ax -o %c").split("\n")
        active = [p for p in self.setting["processes"] if p in processes]

        for p in active:
            LOGGER.debug("process %s" % p)

        return self.stay_awake if active else None
