import logging
import re
import subprocess
from datetime import datetime, timedelta
from sys import platform

from checkers.abstractinterruptionchecker import \
    AbstractInterruptionChecker

LOGGER = logging.getLogger()


class WhoInterruptionChecker(AbstractInterruptionChecker):

    def _who(self) -> 'list[tuple[str,str,str]]':

        LOGGER.debug("query who's logged in")

        ignore_lines = self.setting["ignore_lines"] if "ignore_lines" in self.setting else list(
        )

        lines = subprocess.getoutput("who").splitlines()
        who_list = list()
        for line in lines:
            m = re.match(r"^([^ ]+) +([^ ]+) +(.*)$", line)
            if m and m.groups()[1] not in ignore_lines:
                who_list.append(
                    (m.groups()[0], m.groups()[1], m.groups()[2]))

        return who_list

    def get_occupation(self, dt_now: datetime) -> timedelta:

        if not platform.startswith("linux"):
            return None

        who = self._who()
        if who:
            for w in who:
                LOGGER.debug("user=%s, line=%s, info=%s" % w)
            return self.stay_awake

        else:
            return None
