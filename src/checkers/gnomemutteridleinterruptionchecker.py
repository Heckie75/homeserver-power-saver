import logging
import os
import pwd
import re
import subprocess
from datetime import datetime, timedelta
from sys import platform

from checkers.abstractinterruptionchecker import AbstractInterruptionChecker

LOGGER = logging.getLogger()


class GnomeMutterIdleInterruptionChecker(AbstractInterruptionChecker):

    def get_occupation(self, dt_now: datetime) -> timedelta:

        if not platform.startswith("linux"):
            LOGGER.debug("Skipping Mutter idle check on platform %s", platform)
            return None

        report = self._get_all_users_idle_status()
        LOGGER.debug("Mutter idle status for graphical users: %s", report)
        min_idle = min([user["idle_seconds"]
                       for user in report if user["idle_seconds"] is not None])
        stay_awake_seconds = self.setting["stay_awake"] * 60

        if min_idle is not None and min_idle < stay_awake_seconds:
            remaining = stay_awake_seconds - min_idle
            LOGGER.debug(
                "Minimum idle time %.2f s is below the %.2f s threshold; "
                "keeping the server awake for %.2f s",
                min_idle, stay_awake_seconds, remaining)
            return timedelta(seconds=remaining)

        LOGGER.debug(
            "Minimum idle time %.2f s meets the %.2f s threshold; "
            "the server may sleep",
            min_idle, stay_awake_seconds)
        return None

    def _get_active_graphical_users(self) -> dict[str, int]:
        """
        Returns a dictionary of active graphical users mapping username to their UID.
        """
        users = {}
        try:
            result = subprocess.run(
                ["loginctl", "list-sessions", "--no-legend"],
                capture_output=True, text=True, check=True
            )
            LOGGER.debug("loginctl listed sessions: %s", result.stdout.strip())

            for line in result.stdout.strip().splitlines():
                if not line.strip():
                    continue

                session_id = line.split()[0]

                prop_result = subprocess.run(
                    ["loginctl", "show-session", session_id,
                        "--property=Name", "--property=Type"],
                    capture_output=True, text=True, check=True
                )

                props = {}
                for prop_line in prop_result.stdout.strip().splitlines():
                    if "=" in prop_line:
                        k, v = prop_line.split("=", 1)
                        props[k] = v

                if props.get("Type") in ["wayland", "x11"] and props.get("Name"):
                    username = props.get("Name")
                    try:
                        uid = pwd.getpwnam(username).pw_uid
                        users[username] = uid
                        LOGGER.debug(
                            "Found graphical session for user %s (uid %s)",
                            username, uid)
                    except KeyError:
                        LOGGER.debug(
                            "Skipping graphical session for unknown user %s",
                            username)
                        continue
                else:
                    LOGGER.debug(
                        "Skipping non-graphical session %s with properties %s",
                        session_id, props)

        except Exception as e:
            LOGGER.error(f"Error fetching sessions via loginctl: {e}")

        LOGGER.debug("Active graphical users: %s", users)
        return users

    def _get_user_idle_seconds(self, username: str, uid: int) -> float | None:
        """
        Queries Mutter's IdleMonitor for a specific user and returns idle time in seconds.
        """
        bus_socket = f"/run/user/{uid}/bus"
        if not os.path.exists(bus_socket):
            LOGGER.debug(
                "Skipping Mutter idle query for %s: session bus %s is missing",
                username, bus_socket)
            return None

        dbus_address = f"unix:path={bus_socket}"

        cmd = [
            "runuser", "-u", username, "--",
            "env", f"DBUS_SESSION_BUS_ADDRESS={dbus_address}",
            "gdbus", "call", "--session",
            "--dest", "org.gnome.Mutter.IdleMonitor",
            "--object-path", "/org/gnome/Mutter/IdleMonitor/Core",
            "--method", "org.gnome.Mutter.IdleMonitor.GetIdletime"
        ]

        try:
            result = subprocess.run(
                cmd, capture_output=True, text=True, check=True, timeout=5)
            match = re.search(r'uint64\s+(\d+)', result.stdout)
            if match:
                ms = int(match.group(1))
                LOGGER.debug(
                    f"Idle time for {username}: {(ms / 1000.0):.3f} s")
                return round(ms / 1000.0, 2)
            LOGGER.debug(
                "Mutter idle response for %s did not contain an idle time: %s",
                username, result.stdout.strip())
        except subprocess.TimeoutExpired:
            LOGGER.error(f"Timeout querying idle time for {username}")
        except Exception as e:
            LOGGER.error(f"Error querying idle time for {username}: {e}")

        return None

    def _get_all_users_idle_status(self) -> list[dict]:
        """
        Finds all logged-in graphical users and returns their inactivity status.
        """

        ignore = self.setting.get("ignore")
        ignore_pattern = re.compile(ignore) if ignore is not None else None

        active_users = self._get_active_graphical_users()
        report = []

        for username, uid in active_users.items():
            if ignore_pattern is not None and ignore_pattern.search(username):
                LOGGER.debug("Ignoring graphical user %s by configured pattern",
                             username)
                continue

            idle_secs = self._get_user_idle_seconds(username, uid)
            report.append({
                "user": username,
                "uid": uid,
                "idle_seconds": idle_secs
            })

        return report
