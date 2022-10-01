import unittest
from datetime import timedelta

from utils.period import Period

class TestPeriod(unittest.TestCase):

    def test_miss_after(self):
        """
        p1: |---------|
        ts:                x
            t1        t2   t3
        """

        t1 = timedelta(days=0, hours=1, minutes=0)
        t2 = timedelta(days=0, hours=2, minutes=0)
        ts = timedelta(days=0, hours=3, minutes=0)

        p1 = Period(t1, t2)

        s, e = p1.hit(ts)
        self.assertIsNone(s)
        self.assertIsNone(e)

    def test_miss_before(self):
        """
        p1:                |---------|
        ts:           x
                      t1   t2        t3
        """

        ts = timedelta(days=0, hours=1, minutes=0)
        t2 = timedelta(days=0, hours=2, minutes=0)
        t3 = timedelta(days=0, hours=3, minutes=0)

        p1 = Period(t2, t3)

        s, e = p1.hit(ts)
        self.assertIsNone(s)
        self.assertIsNone(e)

    def test_hit(self):
        """
        p1: |---------|
        p2:       x
            t1    t2  t3
        """

        t1 = timedelta(days=0, hours=1, minutes=0)
        ts = timedelta(days=0, hours=2, minutes=0)
        t3 = timedelta(days=0, hours=3, minutes=0)

        p1 = Period(t1, t3)

        s, e = p1.hit(ts)
        self.assertEqual(s, timedelta(hours=-1))
        self.assertEqual(e, timedelta(hours=1))

    def test_hit_touches_start(self):
        """
        p1: |---------|
        p2: x
            t1        t2
        """
        t1 = timedelta(days=0, hours=1, minutes=0)
        t2 = timedelta(days=0, hours=2, minutes=0)

        p1 = Period(t1, t2)

        s, e = p1.hit(t1)
        self.assertEqual(s, timedelta())
        self.assertEqual(e, timedelta(hours=1))

    def test_hit_touches_end(self):
        """
        p1: |---------|
        p2:           x
            t1        t2
        """
        t1 = timedelta(days=0, hours=1, minutes=0)
        t2 = timedelta(days=0, hours=2, minutes=0)

        p1 = Period(t1, t2)

        s, e = p1.hit(t2)
        self.assertEqual(s, timedelta(hours=-1))
        self.assertEqual(e, timedelta())
