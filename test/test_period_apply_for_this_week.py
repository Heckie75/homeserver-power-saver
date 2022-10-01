import unittest
from datetime import datetime, timedelta

from utils.period import Period
from utils.periods import Periods


class TestPeriods(unittest.TestCase):

    def test_apply_for_this_week(self):
        """
        p1   ---|                                                        |---
        p2      t1 |-----|                                               t10
        p3         t2    t3    |--|     t7
        p4                     t4 t5 |--|  t8                t9
        p5                           t6    |-----------------|
             |--+--+--|--+--+--|--+--+--|--+--+--|--+--+--|--+--+--|--+--+--|
               x0 x1 x2 x3  x4  x5  x6 x7 x8  x9    x10    x11  x12  x13  x14
        """

        t1 = timedelta(days=0, hours=8)
        t2 = timedelta(days=0, hours=16)
        t3 = timedelta(days=1, hours=8)
        t4 = timedelta(days=2, hours=0)
        t5 = timedelta(days=2, hours=8)
        t6 = timedelta(days=2, hours=16)
        t7 = timedelta(days=3, hours=0)
        t8 = timedelta(days=3, hours=8)
        t9 = timedelta(days=5, hours=8)
        t10 = timedelta(days=6, hours=16)

        periods = Periods()
        p1 = Period(t10, t1)
        p2 = Period(t2, t3)
        p3 = Period(t4, t5)
        p4 = Period(t6, t7)
        p5 = Period(t8, t9)
        for p in [p1, p2, p3, p4, p5]:
            periods.add(p)

        x0 = datetime(year=2022, month=12, day=5, hour=6)
        self.assertEquals(str(p1.apply_for_this_week(x0)),
                          "2022-12-04 16:00:00 -> 2022-12-05 08:00:00")

        x1 = datetime(year=2022, month=12, day=5, hour=12)
        self.assertEquals(str(p2.apply_for_this_week(x1)),
                          "2022-12-05 16:00:00 -> 2022-12-06 08:00:00")

        x2 = datetime(year=2022, month=12, day=5, hour=22)
        self.assertEquals(str(p2.apply_for_this_week(x2)),
                          "2022-12-05 16:00:00 -> 2022-12-06 08:00:00")

        x3 = datetime(year=2022, month=12, day=6, hour=4)
        self.assertEquals(str(p2.apply_for_this_week(x3)),
                          "2022-12-05 16:00:00 -> 2022-12-06 08:00:00")

        x4 = datetime(year=2022, month=12, day=6, hour=16)
        self.assertEquals(str(p3.apply_for_this_week(x4)),
                          "2022-12-07 00:00:00 -> 2022-12-07 08:00:00")

        x5 = datetime(year=2022, month=12, day=7, hour=4)
        self.assertEquals(str(p3.apply_for_this_week(x5)),
                          "2022-12-07 00:00:00 -> 2022-12-07 08:00:00")

        x6 = datetime(year=2022, month=12, day=7, hour=12)
        self.assertEquals(str(p4.apply_for_this_week(x6)),
                          "2022-12-07 16:00:00 -> 2022-12-08 00:00:00")

        x7 = datetime(year=2022, month=12, day=7, hour=22)
        self.assertEquals(str(p4.apply_for_this_week(x7)),
                          "2022-12-07 16:00:00 -> 2022-12-08 00:00:00")

        x8 = datetime(year=2022, month=12, day=8, hour=4)
        self.assertEquals(str(p5.apply_for_this_week(x8)),
                          "2022-12-08 08:00:00 -> 2022-12-10 08:00:00")

        x9 = datetime(year=2022, month=12, day=8, hour=16)
        self.assertEquals(str(p5.apply_for_this_week(x9)),
                          "2022-12-08 08:00:00 -> 2022-12-10 08:00:00")

        x10 = datetime(year=2022, month=12, day=9, hour=8)
        self.assertEquals(str(p5.apply_for_this_week(x10)),
                          "2022-12-08 08:00:00 -> 2022-12-10 08:00:00")

        x11 = datetime(year=2022, month=12, day=10, hour=4)
        self.assertEquals(str(p5.apply_for_this_week(x11)),
                          "2022-12-08 08:00:00 -> 2022-12-10 08:00:00")

        x12 = datetime(year=2022, month=12, day=10, hour=16)
        self.assertEquals(str(p1.apply_for_this_week(x12)),
                          "2022-12-11 16:00:00 -> 2022-12-12 08:00:00")

        x13 = datetime(year=2022, month=12, day=11, hour=8)
        self.assertEquals(str(p1.apply_for_this_week(x13)),
                          "2022-12-11 16:00:00 -> 2022-12-12 08:00:00")

        x14 = datetime(year=2022, month=12, day=11, hour=20)
        self.assertEquals(str(p1.apply_for_this_week(x14)),
                          "2022-12-11 16:00:00 -> 2022-12-12 08:00:00")
