import unittest
from datetime import datetime, timedelta
from unittest.mock import patch

from checkers.whointerruptionchecker import WhoInterruptionChecker


class TestWhoInteruptionsChecker(unittest.TestCase):

    @patch("checkers.whointerruptionchecker.subprocess.getoutput")
    def test_unignored_line_means_busy(self, getoutput):

        getoutput.return_value = "an output line without parsed terminal columns"

        setting = {
            "enable": True,
            "ignore": r"tty[0-9]+$",
            "stay_awake": 5
        }

        checker = WhoInterruptionChecker(setting=setting)

        busy = checker.get_occupation(datetime.today())
        self.assertEqual(busy, timedelta(minutes=5))

    @patch("checkers.whointerruptionchecker.subprocess.getoutput")
    def test_lines_matching_ignore_regex_are_not_busy(self, getoutput):

        getoutput.return_value = (
            "heckie tty7 :0 session\n"
            "heckie seat0 :0 session"
        )

        checker = WhoInterruptionChecker(setting={
            "enable": True,
            "ignore": r"\b(?:tty7|seat0)\b",
            "stay_awake": 5
        })

        busy = checker.get_occupation(datetime.today())
        self.assertIsNone(busy)
