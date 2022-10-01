import logging
import subprocess
from datetime import datetime, timedelta
from sys import platform

from checkers.abstractinterruptionchecker import \
    AbstractInterruptionChecker

LOGGER = logging.getLogger()


class PingInterruptionChecker(AbstractInterruptionChecker):

    def _ping(self, ip) -> bool:

        LOGGER.debug("try to ping %s" % ip)

        with subprocess.Popen(["ping", "-w", "1", "-c", "1", ip], stdin=subprocess.PIPE, stdout=subprocess.PIPE) as p:
            out, err = p.communicate()
            if out:
                LOGGER.debug(out.decode("utf-8"))

            if err:
                LOGGER.debug(err.decode("utf-8"))

            return p.returncode == 0

    def get_occupation(self, dt_now: datetime) -> timedelta:

        if not platform.startswith("linux"):
            return None

        available_ips = [ip for ip in self.setting["ip"] if self._ping(ip)]

        if available_ips:
            for ip in available_ips:
                LOGGER.debug(ip)
            return self.stay_awake

        else:
            return None
