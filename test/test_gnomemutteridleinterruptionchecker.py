import subprocess
import unittest
from datetime import datetime, timedelta
from types import SimpleNamespace
from unittest.mock import patch

from checkers.gnomemutteridleinterruptionchecker import (
    GnomeMutterIdleInterruptionChecker,
)
from powersaver.powersaver import PowerSaver


class TestGnomeMutterIdleInterruptionChecker(unittest.TestCase):

    def test_enabled_checker_is_loaded_by_power_saver(self):
        power_saver = PowerSaver({
            "respite_prepare": 0,
            "respite_recover": 0,
            "mode": "mem",
            "dryrun": True,
            "checkers": {
                "GnomeMutterIdleInterruptionChecker": {
                    "enable": True,
                    "stay_awake": 5,
                },
            },
        })

        self.assertEqual(len(power_saver._checkers), 1)
        self.assertIsInstance(
            power_saver._checkers[0], GnomeMutterIdleInterruptionChecker)

    def test_recently_active_graphical_user_keeps_server_awake(self):
        checker = GnomeMutterIdleInterruptionChecker({"stay_awake": 5})
        now = datetime(2026, 10, 17, 20, 0)
        command_results = [
            subprocess.CompletedProcess(
                args=[], returncode=0, stdout="1 user seat0\n", stderr=""),
            subprocess.CompletedProcess(
                args=[], returncode=0,
                stdout="Name=heckie\nType=wayland\n", stderr=""),
            subprocess.CompletedProcess(
                args=[], returncode=0, stdout="(uint64 120000,)\n", stderr=""),
        ]

        with (
            patch(
                "checkers.gnomemutteridleinterruptionchecker.platform",
                "linux"),
            patch(
                "checkers.gnomemutteridleinterruptionchecker.subprocess.run",
                side_effect=command_results) as run,
            patch(
                "checkers.gnomemutteridleinterruptionchecker.pwd.getpwnam",
                return_value=SimpleNamespace(pw_uid=1000)),
            patch(
                "checkers.gnomemutteridleinterruptionchecker.os.path.exists",
                return_value=True),
        ):
            occupation = checker.get_occupation(now)

        self.assertEqual(occupation, timedelta(minutes=3))
        self.assertEqual(run.call_count, 3)
        self.assertEqual(
            run.call_args_list[0].args[0],
            ["loginctl", "list-sessions", "--no-legend"])
        self.assertEqual(
            run.call_args_list[1].args[0],
            ["loginctl", "show-session", "1",
             "--property=Name", "--property=Type"])
        self.assertEqual(run.call_args_list[2].kwargs["timeout"], 5)
