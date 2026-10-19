import logging
import subprocess
import time
from datetime import datetime, timedelta
from sys import platform

from checkers.abstractinterruptionchecker import \
    AbstractInterruptionChecker

LOGGER = logging.getLogger()


class WaylandInterruptionChecker(AbstractInterruptionChecker):

    def _loginctl(self, *args: str) -> str:

        LOGGER.debug("loginctl %s" % " ".join(args))
        result = subprocess.run(
            ["loginctl", *args],
            check=True,
            capture_output=True,
            text=True,
            timeout=5)

        LOGGER.debug(result.stdout)
        return result.stdout

    def _show_properties(self, output: str) -> dict[str, str]:

        properties = {}
        for line in output.splitlines():
            key, separator, value = line.partition("=")
            if separator:
                properties[key] = value
        return properties

    def get_occupation(self, dt_now: datetime) -> timedelta:

        if not platform.startswith("linux"):
            return None

        try:
            min_idle_seconds = self.setting.get("min_idle", 0) * 60
            for user in self.setting["users"]:
                session_ids = self._loginctl(
                    "show-user", user, "--property=Sessions", "--value").split()

                for session_id in session_ids:
                    properties = self._show_properties(self._loginctl(
                        "show-session", session_id,
                        "--property=Type",
                        "--property=Active",
                        "--property=IdleHint",
                        "--property=IdleSinceHintMonotonic"))

                    if properties.get("Type") != "wayland" or properties.get("Active") != "yes":
                        continue

                    idle_hint = properties.get("IdleHint")
                    if idle_hint == "no":
                        LOGGER.debug(
                            "User %s has an active Wayland session.", user)
                        return self.stay_awake
                    if idle_hint != "yes":
                        raise RuntimeError(
                            "loginctl did not report an IdleHint for Wayland session %s"
                            % session_id)

                    idle_since = properties.get("IdleSinceHintMonotonic")
                    if not idle_since or int(idle_since) <= 0:
                        raise RuntimeError(
                            "loginctl did not report when Wayland session %s became idle"
                            % session_id)

                    idle_seconds = max(
                        0, time.monotonic() - int(idle_since) / 1_000_000)
                    if idle_seconds < min_idle_seconds:
                        LOGGER.debug(
                            "User %s has been idle for %.1f minutes; threshold is %i minutes.",
                            user, idle_seconds / 60,
                            self.setting.get("min_idle", 0))
                        return self.stay_awake

            return None
        except (OSError, subprocess.SubprocessError, RuntimeError,
                ValueError) as error:
            LOGGER.warning(
                "%s: Unable to reliably check Wayland activity; "
                "allowing the server to sleep: %s",
                self.__class__.__name__, " ".join(str(error).splitlines()))
            return None
