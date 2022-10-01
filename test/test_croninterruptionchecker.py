import unittest
from datetime import datetime
from crontab import CronTab

from checkers.croninterruptionchecker import CronInterruptionChecker


class MockedCronInterruptionChecker(CronInterruptionChecker):

    def _get_crontabs(self) -> 'list[CronTab]':

        tab = CronTab(tab="""
0 20 * * *  echo command 1
15 10 * * 4 echo command 2
0 1 * * 1   echo command 3
""")

        return [tab]


class TestCronInterruptionChecker(unittest.TestCase):

    def test_croninterruptionchecker(self):

        setting = {
            "enable": True,
            "stay_awake": 5,
            "extra_wakeup_time": 3,
            "users": [
                "heckie",
                "root"
            ],
            "tabfiles": [],
            "ignore_frequency": {
                "max_per_year": 365
            }
        }

        croninteruptionchecker = MockedCronInterruptionChecker(setting)

        dt_now = datetime(year=2022, month=12, day=22, hour=8, minute=25)
        croninteruptionchecker.get_occupation(dt_now)
        td = croninteruptionchecker.get_upcoming_event(dt_now)
        self.assertEquals(td, datetime(2022, 12, 22, 10, 15))

        dt_now = datetime(year=2022, month=12, day=22, hour=10, minute=25)
        croninteruptionchecker.get_occupation(dt_now)
        td = croninteruptionchecker.get_upcoming_event(dt_now)
        self.assertEquals(td, datetime(2022, 12, 22, 20, 0))

        dt_now = datetime(year=2022, month=12, day=22, hour=14, minute=27)
        croninteruptionchecker.get_occupation(dt_now)
        td = croninteruptionchecker.get_upcoming_event(dt_now)
        self.assertEquals(td, datetime(2022, 12, 22, 20, 0))

        dt_now = datetime(year=2022, month=12, day=25, hour=23, minute=27)
        croninteruptionchecker.get_occupation(dt_now)
        td = croninteruptionchecker.get_upcoming_event(dt_now)
        self.assertEquals(td, datetime(2022, 12, 26, 1, 0))
