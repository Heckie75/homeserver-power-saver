import subprocess
import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from checkers.waylandinterruptionchecker import WaylandInterruptionChecker


class TestWaylandInterruptionChecker(unittest.TestCase):

    def setUp(self):
        self.checker = WaylandInterruptionChecker({
            "users": ["heckie"],
            "min_idle": 10,
            "stay_awake": 5,
        })
        self.now = datetime(2026, 10, 11, 10, 0)

    @patch("checkers.waylandinterruptionchecker.platform", "linux")
    @patch("checkers.waylandinterruptionchecker.subprocess.run")
    def test_recently_active_wayland_session_keeps_server_awake(self, run):
        run.side_effect = [
            subprocess.CompletedProcess(
                args=[], returncode=0, stdout="4\n", stderr=""),
            subprocess.CompletedProcess(
                args=[], returncode=0,
                stdout="Type=wayland\nActive=yes\nIdleHint=no\n"
                       "IdleSinceHintMonotonic=0\n", stderr=""),
        ]

        self.assertEqual(
            self.checker.get_occupation(self.now), timedelta(minutes=5))
        self.assertEqual(run.call_count, 2)
        self.assertEqual(run.call_args_list[0].args[0][:3],
                         ["loginctl", "show-user", "heckie"])
        self.assertEqual(run.call_args_list[1].args[0][:3],
                         ["loginctl", "show-session", "4"])

    @patch("checkers.waylandinterruptionchecker.platform", "linux")
    @patch("checkers.waylandinterruptionchecker.time.monotonic", return_value=1000)
    @patch("checkers.waylandinterruptionchecker.subprocess.run")
    def test_idle_below_threshold_keeps_server_awake(
            self, run, _monotonic):
        run.side_effect = [
            subprocess.CompletedProcess(
                args=[], returncode=0, stdout="4\n", stderr=""),
            subprocess.CompletedProcess(
                args=[], returncode=0,
                stdout="Type=wayland\nActive=yes\nIdleHint=yes\n"
                       "IdleSinceHintMonotonic=950000000\n", stderr=""),
        ]

        self.assertEqual(
            self.checker.get_occupation(self.now), timedelta(minutes=5))

    @patch("checkers.waylandinterruptionchecker.platform", "linux")
    @patch("checkers.waylandinterruptionchecker.time.monotonic", return_value=1000)
    @patch("checkers.waylandinterruptionchecker.subprocess.run")
    def test_idle_above_threshold_allows_sleep(self, run, _monotonic):
        run.side_effect = [
            subprocess.CompletedProcess(
                args=[], returncode=0, stdout="Sessions=4\n", stderr=""),
            subprocess.CompletedProcess(
                args=[], returncode=0,
                stdout="Type=wayland\nActive=yes\nIdleHint=yes\n"
                       "IdleSinceHintMonotonic=100000000\n", stderr=""),
        ]

        self.assertIsNone(self.checker.get_occupation(self.now))

    @patch("checkers.waylandinterruptionchecker.platform", "linux")
    @patch("checkers.waylandinterruptionchecker.subprocess.run")
    def test_non_wayland_session_is_ignored(self, run):
        run.side_effect = [
            subprocess.CompletedProcess(
                args=[], returncode=0, stdout="Sessions=4\n", stderr=""),
            subprocess.CompletedProcess(
                args=[], returncode=0,
                stdout="Type=x11\nActive=yes\nIdleHint=no\n"
                       "IdleSinceHintMonotonic=0\n", stderr=""),
        ]

        self.assertIsNone(self.checker.get_occupation(self.now))

    @patch("checkers.waylandinterruptionchecker.subprocess.run",
           side_effect=FileNotFoundError("loginctl not found"))
    def test_login_manager_failure_allows_sleep(self, _run):

        with self.assertLogs(level="WARNING") as logs:
            occupation = self.checker._get_occupation(self.now)

        self.assertIsNone(occupation)
        self.assertIn("allowing the server to sleep", logs.output[0])
        self.assertIn("loginctl not found", logs.output[0])

    def test_show_properties_parses_loginctl_output(self):
        properties = self.checker._show_properties(
            "Type=wayland\nActive=yes\nIdleHint=no\n")

        self.assertEqual(properties, {
            "Type": "wayland",
            "Active": "yes",
            "IdleHint": "no",
        })
