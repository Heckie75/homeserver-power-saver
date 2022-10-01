import unittest
from datetime import datetime

from checkers.tvheadendinterruptionchecker import TvHeadendInterruptionChecker


class TestTvHeadendInteruptionChecker(unittest.TestCase):

    def test_tvheadendinteruptionchecker(self):

        setting = {
            "enable": True,
            "host": "192.168.178.30",
            "port": 9981,
            "user": "tvheadenduser",
            "password": "tvheadenduser",
            "pre_recording_time": 5,
            "post_subscription_time": 10
        }

        dt_now = datetime.today()

        tvheadendinteruptionchecker = TvHeadendInterruptionChecker(
            setting=setting)
        busy = tvheadendinteruptionchecker._get_occupation(dt_now)
        wait = tvheadendinteruptionchecker._get_upcoming_event(dt_now)
        self.assertIsNotNone(wait)
