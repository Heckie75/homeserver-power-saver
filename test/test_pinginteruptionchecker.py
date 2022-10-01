import unittest
from datetime import datetime, timedelta
from sys import platform

from checkers.pinginterruptionchecker import PingInterruptionChecker

class TestPingInteruptionsChecker(unittest.TestCase):

    def test_pinginteruption_checker_check_busy(self):

        if not platform.startswith("linux"):
            return

        setting = {
            "enable": True,
            "ip": [
                "127.0.0.1"
            ],
            "ignore_periods": [],
            "stay_awake": 20
        }

        pinginteruption = PingInterruptionChecker(setting=setting)

        dt_now = datetime.today()
        busy = pinginteruption._get_occupation(dt_now)
        self.assertEquals(busy, timedelta(minutes=20))

    def test_pinginteruption_checker_check_not_busy(self):

        if not platform.startswith("linux"):
            return

        setting = {
            "enable": True,
            "ip": [
                "192.168.178.99"
            ],
            "ignore_periods": [],
            "stay_awake": 20
        }

        pinginteruption = PingInterruptionChecker(
            setting=setting)

        dt_now = datetime.today()
        busy = pinginteruption._get_occupation(dt_now)
        self.assertIsNone(busy)

    def test_pinginteruption_checker_check_busy_but_ignore(self):

        if not platform.startswith("linux"):
            return

        setting = {
            "enable": True,
            "ip": [
                "127.0.0.1"
            ],
            "ignore_periods": [
                {
                    "days": [
                        0, 1, 2, 3, 4, 5, 6
                    ],
                    "from": "7:00",
                    "until": "11:00"
                }
            ],
            "stay_awake": 20
        }

        pinginteruption = PingInterruptionChecker(
            setting=setting)

        busy = pinginteruption._get_occupation(datetime(year=2022, month=12, day=22, hour=9))
        self.assertIsNone(busy)
