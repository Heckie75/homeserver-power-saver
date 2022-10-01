import unittest
from datetime import datetime, timedelta

from checkers.kodiinterruptionchecker import KodiInterruptionChecker
from utils.period import Period


class TestKodiInteruptionChecker(unittest.TestCase):

    def test_kodiinteruptionchecker(self):

        setting = {
            "enable": True,
            "host": "192.168.178.30",
            "port": 9080,
            "user": "kodi",
            "password": "kodi",
            "post_active_time": 10
        }

        dt_now = datetime.today()

        period = Period(timedelta(), timedelta(days=8))
        kodiinteruptionchecker = KodiInterruptionChecker(
            setting=setting)

        kodiinteruptionchecker.get_occupation(dt_now)
        kodiinteruptionchecker.get_upcoming_event(dt_now)
        self.assertTrue(True)
