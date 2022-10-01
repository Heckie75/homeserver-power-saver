import unittest
from datetime import datetime, timedelta

from utils.period import Period
from utils.periods import Periods


class TestPeriods(unittest.TestCase):

    def test_append_from_settings(self):

        setting = [
            {
                "days": [
                    0,
                    1,
                    2,
                    3,
                    4,
                    5,
                    6
                ],
                "from": "22:15",
                "until": "06:45"
            },
            {
                "days": [
                    0,
                    1,
                    2,
                    3,
                    4
                ],
                "from": "08:15",
                "until": "19:25"
            }
        ]

        p = Periods()
        p.append_from_settings(setting)

        periods = p.periods

        for i in range(5):
            self.assertEquals(periods[2 * i].start,
                              timedelta(hours=8, minutes=15, days=i))
            self.assertEquals(periods[2 * i].end,
                              timedelta(hours=19, minutes=25, days=i))
            self.assertEquals(periods[2 * i + 1].start,
                              timedelta(hours=22, minutes=15, days=i))
            self.assertEquals(periods[2 * i + 1].end,
                              timedelta(hours=6, minutes=45, days=i + 1))

        self.assertEquals(periods[10].start, timedelta(
            hours=22, minutes=15, days=5))
        self.assertEquals(periods[10].end, timedelta(
            hours=6, minutes=45, days=6))
        self.assertEquals(periods[11].start, timedelta(
            hours=22, minutes=15, days=6))
        self.assertEquals(periods[11].end, timedelta(
            hours=6, minutes=45, days=0))

    def test_add(self):

        periods = Periods()
        periods.add(Period(timedelta(days=1, hours=22),
                    timedelta(days=1, hours=23)))

        self.assertEquals(len(periods.periods), 1)
        self.assertEquals(periods.periods[
                          0].start, timedelta(days=1, hours=22))

    def test_unify_1(self):

        periods = Periods()
        periods.add(Period(timedelta(days=0, hours=11),
                    timedelta(days=0, hours=13)))
        periods.add(Period(timedelta(days=0, hours=10),
                    timedelta(days=0, hours=12)))

        periods.unify()

        self.assertEquals(len(periods.periods), 1)
        self.assertEquals(periods.periods[
                          0].start, timedelta(days=0, hours=10))
        self.assertEquals(periods.periods[
                          0].end, timedelta(days=0, hours=13))

    def test_unify_2(self):

        periods = Periods()
        periods.add(Period(timedelta(days=6, hours=23),
                    timedelta(days=0, hours=2)))
        periods.add(Period(timedelta(days=0, hours=1),
                    timedelta(days=0, hours=3)))

        periods.unify()

        self.assertEquals(len(periods.periods), 1)
        self.assertEquals(periods.periods[
                          0].start, timedelta(days=6, hours=23))
        self.assertEquals(periods.periods[
                          0].end, timedelta(days=0, hours=3))

    def test_unify_3(self):

        periods = Periods()
        periods.add(Period(timedelta(days=6, hours=21),
                    timedelta(days=6, hours=23)))
        periods.add(Period(timedelta(days=6, hours=22),
                    timedelta(days=0, hours=3)))

        periods.unify()

        self.assertEquals(len(periods.periods), 1)
        self.assertEquals(periods.periods[
                          0].start, timedelta(days=6, hours=21))
        self.assertEquals(periods.periods[
                          0].end, timedelta(days=0, hours=3))

    def test_get_next_period_1(self):
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
        running, period = periods.get_next_period(x0)
        self.assertEquals(
            str(period), "2022-12-04 16:00:00 -> 2022-12-05 08:00:00")
        self.assertTrue(running)

        x1 = datetime(year=2022, month=12, day=5, hour=12)
        running, period = periods.get_next_period(x1)
        self.assertEquals(
            str(period), "2022-12-05 16:00:00 -> 2022-12-06 08:00:00")
        self.assertFalse(running)

        x2 = datetime(year=2022, month=12, day=5, hour=22)
        running, period = periods.get_next_period(x2)
        self.assertEquals(
            str(period), "2022-12-05 16:00:00 -> 2022-12-06 08:00:00")
        self.assertTrue(running)

        x3 = datetime(year=2022, month=12, day=6, hour=4)
        running, period = periods.get_next_period(x3)
        self.assertEquals(
            str(period), "2022-12-05 16:00:00 -> 2022-12-06 08:00:00")
        self.assertTrue(running)

        x4 = datetime(year=2022, month=12, day=6, hour=16)
        running, period = periods.get_next_period(x4)
        self.assertEquals(
            str(period), "2022-12-07 00:00:00 -> 2022-12-07 08:00:00")
        self.assertFalse(running)

        x5 = datetime(year=2022, month=12, day=7, hour=4)
        running, period = periods.get_next_period(x5)
        self.assertEquals(
            str(period), "2022-12-07 00:00:00 -> 2022-12-07 08:00:00")
        self.assertTrue(running)

        x6 = datetime(year=2022, month=12, day=7, hour=12)
        running, period = periods.get_next_period(x6)
        self.assertEquals(
            str(period), "2022-12-07 16:00:00 -> 2022-12-08 00:00:00")
        self.assertFalse(running)

        x7 = datetime(year=2022, month=12, day=7, hour=22)
        running, period = periods.get_next_period(x7)
        self.assertEquals(
            str(period), "2022-12-07 16:00:00 -> 2022-12-08 00:00:00")
        self.assertTrue(running)

        x8 = datetime(year=2022, month=12, day=8, hour=4)
        running, period = periods.get_next_period(x8)
        self.assertEquals(
            str(period), "2022-12-08 08:00:00 -> 2022-12-10 08:00:00")
        self.assertFalse(running)

        x9 = datetime(year=2022, month=12, day=8, hour=16)
        running, period = periods.get_next_period(x9)
        self.assertEquals(
            str(period), "2022-12-08 08:00:00 -> 2022-12-10 08:00:00")
        self.assertTrue(running)

        x10 = datetime(year=2022, month=12, day=9, hour=8)
        running, period = periods.get_next_period(x10)
        self.assertEquals(
            str(period), "2022-12-08 08:00:00 -> 2022-12-10 08:00:00")
        self.assertTrue(running)

        x11 = datetime(year=2022, month=12, day=10, hour=4)
        running, period = periods.get_next_period(x11)
        self.assertEquals(
            str(period), "2022-12-08 08:00:00 -> 2022-12-10 08:00:00")
        self.assertTrue(running)

        x12 = datetime(year=2022, month=12, day=10, hour=16)
        running, period = periods.get_next_period(x12)
        self.assertEquals(
            str(period), "2022-12-11 16:00:00 -> 2022-12-12 08:00:00")
        self.assertFalse(running)

        x13 = datetime(year=2022, month=12, day=11, hour=8)
        running, period = periods.get_next_period(x13)
        self.assertEquals(
            str(period), "2022-12-11 16:00:00 -> 2022-12-12 08:00:00")
        self.assertFalse(running)

        x14 = datetime(year=2022, month=12, day=11, hour=20)
        running, period = periods.get_next_period(x14)
        self.assertEquals(
            str(period), "2022-12-11 16:00:00 -> 2022-12-12 08:00:00")
        self.assertTrue(running)
