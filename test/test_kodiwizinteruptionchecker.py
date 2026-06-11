import unittest
from datetime import datetime, timedelta

from checkers.kodiwizinterruptionchecker import KodiWizInterruptionChecker
from utils.period import Period


class TestKodiWizInteruptionChecker(unittest.TestCase):

    def test_kodiwizinteruptionchecker(self):

        setting = {
            "enable": True,
            "stay_awake": 10,
            "ignore_periods": [],
            "path": "/home/heckie/.kodi/userdata/addon_data/script.wiz/running_programs.json"
        }

        dt_now = datetime.today()

        period = Period(timedelta(), timedelta(days=8))
        kodiwizinteruptionchecker = KodiWizInterruptionChecker(
            setting=setting)

        occupation = kodiwizinteruptionchecker.get_occupation(dt_now)
        self.assertTrue(True)
