import unittest
from datetime import datetime

from utils import datetimeutils


class TestGlobals(unittest.TestCase):

    def test_format_datetime(self):

        s = datetimeutils.format_datetime(
            datetime(year=2022, month=10, day=3, hour=8, minute=15, second=45))
        self.assertEqual("2022-10-03 08:15:45", s)
