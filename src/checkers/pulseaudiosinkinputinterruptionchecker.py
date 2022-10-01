import json
import logging
import os
import subprocess
from datetime import datetime, timedelta
from sys import platform

from checkers.abstractinterruptionchecker import \
    AbstractInterruptionChecker

LOGGER = logging.getLogger()


class PulseAudioSinkInputInterruptionChecker(AbstractInterruptionChecker):

    def _get_sink_inputs(self, user: str) -> 'list[dict]':

        LOGGER.debug(
            "get sink inputs for user %s" % user)
        try:
            runuser = "runuser -u %s -- " % user if os.getuid() == 0 else ""
            output = subprocess.getoutput(
                "LANG=en XDG_RUNTIME_DIR=/run/user/$(id -u %s)/ %spactl -f json list sink-inputs" % (user, runuser))
            return json.loads(output) if output else None
        except:
            LOGGER.error("unable to determine sink-inputs", exc_info=True)
            return []

    def get_occupation(self, dt_now: datetime) -> timedelta:

        if not platform.startswith("linux"):
            return None

        for user in self.setting["users"]:
            sink_inputs = self._get_sink_inputs(user)
            if sink_inputs:
                for si in sink_inputs:
                    LOGGER.debug("User %s: %s" %
                                 (user, si["properties"]["media.name"]))
                return self.stay_awake

        return None
