import unittest
from datetime import datetime, timedelta
from sys import platform

from checkers.whointerruptionchecker import WhoInterruptionChecker


class TestWhoInteruptionsChecker(unittest.TestCase):

    def test_whointeruption_checker_check_busy(self):

        if not platform.startswith("linux"):

            return

        setting = {
            "enable": True,
            "ignore_lines": [],
            "stay_awake": 5
        }

        whointeruption = WhoInterruptionChecker(setting=setting)

        busy = whointeruption._get_occupation(datetime.today())
        self.assertEquals(busy, timedelta(minutes=5))

    def test_whointeruption_checker_check_not_busy(self):

        if not platform.startswith("linux"):

            return

        ignore = ["tty%i" % i for i in range(20)]
        ignore.extend(["pts/%i" % i for i in range(20)])

        setting = {
            "enable": True,
            "ignore_lines": ignore,
            "stay_awake": 5
        }

        whointeruption = WhoInterruptionChecker(setting=setting)

        td_now = timedelta(days=0, hours=8)
        busy = whointeruption._get_occupation(datetime.today())
        self.assertIsNone(busy)
