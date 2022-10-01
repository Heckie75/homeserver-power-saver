import logging
import subprocess
from datetime import datetime, timedelta
from sys import platform

from checkers.abstractinterruptionchecker import \
    AbstractInterruptionChecker

LOGGER = logging.getLogger()


class XIdleInterruptionChecker(AbstractInterruptionChecker):

    def get_occupation(self, dt_now: datetime) -> timedelta:

        if not platform.startswith("linux"):
            return None

        for user in self.setting["users"]:
            try:
                idle = int(subprocess.getoutput(
                    "sudo -u %s DISPLAY=:0 xprintidle" % user))
                if idle < self.setting["min_idle"] * 60000:
                    LOGGER.debug("User %s has been working with desktop %i minutes ago." % (
                        user, idle // 60000))
                    return self.stay_awake

            except:
                LOGGER.error("Unable to check user %s." % user, exc_info=True)

        return None
