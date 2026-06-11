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

    def test_wizclient(self):

        setting = {
            "enable": True,
            "stay_awake": 5,
            "ignore_periods": [],
            "path": "/home/heckie/.kodi/userdata/addon_data/script.wiz/running_programs.json",
            "halt": True,
            "continue": True,            
            "host": "192.168.178.20",
            "port": 9080,
            "user": "kodi",
            "password": "kodi"
        }

        dt_now = datetime.today()

        period = Period(timedelta(), timedelta(days=8))
        kodiwizinteruptionchecker = KodiWizInterruptionChecker(
            setting=setting)

        kodiwizinteruptionchecker.perform_pre_action(dt_wakeup=dt_now)
        kodiwizinteruptionchecker.perform_post_action()
        self.assertTrue(True)
