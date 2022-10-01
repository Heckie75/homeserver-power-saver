import unittest
from datetime import datetime, timedelta

from checkers.koditimersinterruptionchecker import \
    KodiTimersInterruptionChecker
from utils.period import Period


class MockedKodiTimersInterruptionChecker(KodiTimersInterruptionChecker):

    def _load_timers_json(self):

        return """[
  {
    "days": [
      0,
      1,
      2,
      3,
      4,
      5,
      6,
      7
    ],
    "end": "20:15",
    "end_offset": 0,
    "media_action": 1,
    "media_type": "video",
    "path": "media1.mp3",
    "start": "20:00",
    "start_offset": 0
  },
  {
    "days": [
      3
    ],
    "end": "11:00",
    "end_offset": 0,
    "media_action": 1,
    "media_type": "video",
    "path": "media2.mp3",
    "start": "10:15",
    "start_offset": 0
  },
  {
    "days": [
      0,
      7
    ],
    "end": "02:00",
    "end_offset": 0,    
    "media_action": 1,
    "media_type": "video",
    "path": "media3.mp3",
    "start": "01:00",
    "start_offset": 0
  }
]"""

    def _load_settings_xml(self):

        return """<settings version="2">
    <setting id="pause_date_from" default="true">2001-01-01</setting>
    <setting id="pause_time_from" default="true">00:01</setting>
    <setting id="pause_date_until">2001-01-01</setting>
    <setting id="pause_time_until">00:01</setting>
    <setting id="vol_default">100</setting>
</settings>"""


class TestKodiTimersInteruptionChecker(unittest.TestCase):

    def test_koditimersinteruptionchecker(self):

        setting = {
            "enable": True,
            "path": "/home/heckie/.kodi",
            "extra_wakeup_time": 3,
            "postaction": True,
            "host": "192.168.178.30",
            "port": 9080,
            "user": "kodi",
            "password": "kodi",
        }

        period = Period(
            timedelta(days=3, hours=7, minutes=35), timedelta(days=4, hours=6, minutes=45))
        kodiinteruptionchecker = MockedKodiTimersInterruptionChecker(setting)

        dt_now = datetime(year=2022, month=12, day=22, hour=8, minute=25)
        kodiinteruptionchecker.get_occupation(dt_now)
        td = kodiinteruptionchecker.get_upcoming_event(dt_now)
        self.assertEquals(td, datetime(2022, 12, 22, 10, 15))

        dt_now = datetime(year=2022, month=12, day=22, hour=10, minute=25)
        kodiinteruptionchecker.get_occupation(dt_now)
        td = kodiinteruptionchecker.get_upcoming_event(dt_now)
        self.assertEquals(td, datetime(2022, 12, 22, 20, 0))

        dt_now = datetime(year=2022, month=12, day=22, hour=14, minute=27)
        kodiinteruptionchecker.get_occupation(dt_now)
        td = kodiinteruptionchecker.get_upcoming_event(dt_now)
        self.assertEquals(td, datetime(2022, 12, 22, 20, 0))

        period = Period(
            timedelta(days=6, hours=7, minutes=35), timedelta(days=0, hours=6, minutes=45))
        dt_now = datetime(year=2022, month=12, day=25, hour=23, minute=27)
        kodiinteruptionchecker.get_occupation(dt_now)
        td = kodiinteruptionchecker.get_upcoming_event(dt_now)
        self.assertEquals(td, datetime(2022, 12, 26, 1, 0))

    def test_set_volume(self):

        setting = {
            "enable": True,
            "path": "/home/heckie/.kodi",
            "extra_wakeup_time": 3,
            "postaction": True,
            "host": "192.168.178.30",
            "port": 9080,
            "user": "kodi",
            "password": "kodi",
        }

        kodiinteruptionchecker = MockedKodiTimersInterruptionChecker(setting)
        kodiinteruptionchecker._perform_post_action()
