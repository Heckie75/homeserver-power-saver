import unittest
from datetime import datetime, timedelta

from utils.period import Period


class TestPeriod(unittest.TestCase):

    def test_overlap_before(self):
        """
        p1: |---------|
        p2:                |---------|
            t1        t2   t3        t4
        """

        t1 = timedelta(days=0, hours=1, minutes=0)
        t2 = timedelta(days=0, hours=2, minutes=0)
        t3 = timedelta(days=0, hours=3, minutes=0)
        t4 = timedelta(days=0, hours=4, minutes=0)

        p1 = Period(t1, t2)
        p2 = Period(t3, t4)

        s, e = p1.overlap(p2)
        self.assertIsNone(s)
        self.assertIsNone(e)

    def test_overlap_after(self):
        """
        p1:                |---------|
        p2: |---------|
            t1        t2   t3        t4
        """

        t1 = timedelta(days=0, hours=1, minutes=0)
        t2 = timedelta(days=0, hours=2, minutes=0)
        t3 = timedelta(days=0, hours=3, minutes=0)
        t4 = timedelta(days=0, hours=4, minutes=0)

        p1 = Period(t3, t4)
        p2 = Period(t1, t2)

        s, e = p1.overlap(p2)
        self.assertIsNone(s)
        self.assertIsNone(e)

    def test_overlap_overlap_p2(self):
        """
        p1: |---------|
        p2:       |---------|
            t1    t2  t3    t4
        """

        t1 = timedelta(days=0, hours=1, minutes=0)
        t2 = timedelta(days=0, hours=2, minutes=0)
        t3 = timedelta(days=0, hours=3, minutes=0)
        t4 = timedelta(days=0, hours=4, minutes=0)

        p1 = Period(t1, t3)
        p2 = Period(t2, t4)

        s, e = p1.overlap(p2)
        self.assertEqual(s, timedelta(hours=-1))
        self.assertEqual(e, timedelta(hours=-1))

    def test_overlap_overlap_p1(self):
        """
        p1:       |---------|
        p2: |---------|
            t1    t2  t3    t4
        """
        t1 = timedelta(days=0, hours=1, minutes=0)
        t2 = timedelta(days=0, hours=2, minutes=0)
        t3 = timedelta(days=0, hours=3, minutes=0)
        t4 = timedelta(days=0, hours=4, minutes=0)

        p1 = Period(t2, t4)
        p2 = Period(t1, t3)

        s, e = p1.overlap(p2)
        self.assertEqual(s, timedelta(hours=1))
        self.assertEqual(e, timedelta(hours=1))

    def test_overlap_enclose_p2(self):
        """
        p1: |-----------------|
        p2:     |---------|
            t1  t2        t3  t4
        """
        t1 = timedelta(days=0, hours=1, minutes=0)
        t2 = timedelta(days=0, hours=2, minutes=0)
        t3 = timedelta(days=0, hours=3, minutes=0)
        t4 = timedelta(days=0, hours=4, minutes=0)

        p1 = Period(t1, t4)
        p2 = Period(t2, t3)

        s, e = p1.overlap(p2)
        self.assertEqual(s, timedelta(hours=-1))
        self.assertEqual(e, timedelta(hours=1))

    def test_overlap_enclose_p1(self):
        """
        p1:     |---------|
        p2: |-----------------|
            t1  t2        t3  t4
        """
        t1 = timedelta(days=0, hours=1, minutes=0)
        t2 = timedelta(days=0, hours=2, minutes=0)
        t3 = timedelta(days=0, hours=3, minutes=0)
        t4 = timedelta(days=0, hours=4, minutes=0)

        p1 = Period(t2, t3)
        p2 = Period(t1, t4)

        s, e = p1.overlap(p2)
        self.assertEqual(s, timedelta(hours=1))
        self.assertEqual(e, timedelta(hours=-1))

    def test_overlap_cover(self):
        """
        p1: |---------|
        p2: |---------|
            t1        t2
        """
        t1 = timedelta(days=0, hours=1, minutes=0)
        t2 = timedelta(days=0, hours=2, minutes=0)

        p1 = Period(t1, t2)
        p2 = Period(t1, t2)

        s, e = p1.overlap(p2)
        self.assertEqual(s, timedelta())
        self.assertEqual(e, timedelta())

    def test_apply_for_this_week(self):

        dt_now = datetime.today()

        td = timedelta(days=dt_now.weekday())

        p = Period(td, td)
        p_this_week = p.apply_for_this_week()

        self.assertEqual(datetime.fromtimestamp(p_this_week.start.total_seconds(
        )).strftime("%Y-%m-%d"), dt_now.strftime("%Y-%m-%d"))
        self.assertEqual(datetime.fromtimestamp(p_this_week.end.total_seconds()).strftime(
            "%Y-%m-%d"), dt_now.strftime("%Y-%m-%d"))
