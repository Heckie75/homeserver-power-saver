import unittest
from datetime import datetime

from checkers.abstractinterruptionchecker import AbstractInterruptionChecker
from powersaver.powersaver import PowerSaver


class FailingInterruptionChecker(AbstractInterruptionChecker):

    def get_occupation(self, dt_now):
        raise OSError("checker unavailable")

    def get_upcoming_event(self, dt_now):
        raise OSError("schedule unavailable")


class FailingPostActionChecker(AbstractInterruptionChecker):

    def perform_post_action(self):
        raise RuntimeError("Kodi is unavailable")


class FailingPreActionChecker(AbstractInterruptionChecker):

    def perform_pre_action(self, dt_wakeup):
        raise RuntimeError("pre-action unavailable")


class SuccessfulPostActionChecker(AbstractInterruptionChecker):

    def __init__(self, completed):
        super().__init__({"postaction": True})
        self.completed = completed

    def perform_post_action(self):
        self.completed.append(True)


class SuccessfulPreActionChecker(AbstractInterruptionChecker):

    def __init__(self, completed):
        super().__init__({"preaction": True})
        self.completed = completed

    def perform_pre_action(self, dt_wakeup):
        self.completed.append(dt_wakeup)


class TestCheckerErrorHandling(unittest.TestCase):

    def test_occupation_failure_returns_none(self):

        checker = FailingInterruptionChecker({"stay_awake": 0})
        now = datetime(2026, 10, 11, 10, 0)

        with self.assertLogs(level="WARNING") as logs:
            occupation = checker._get_occupation(now)

        self.assertIsNone(occupation)
        self.assertEqual(len(logs.output), 1)
        self.assertIn("check_occupation failed", logs.output[0])
        self.assertIn("checker unavailable", logs.output[0])

    def test_schedule_failure_returns_none(self):

        checker = FailingInterruptionChecker({})
        now = datetime(2026, 10, 11, 10, 0)

        with self.assertLogs(level="WARNING") as logs:
            event = checker._get_upcoming_event(now)

        self.assertIsNone(event)
        self.assertEqual(len(logs.output), 1)
        self.assertIn("get_upcoming_event failed", logs.output[0])
        self.assertIn("schedule unavailable", logs.output[0])

    def test_post_action_failure_is_logged_and_does_not_stop_later_actions(self):

        completed = []
        powersaver = PowerSaver.__new__(PowerSaver)
        powersaver._respite_recover = 0
        powersaver._checkers = [
            SuccessfulPostActionChecker(completed),
            FailingPostActionChecker({"postaction": True}),
        ]

        with self.assertLogs(level="WARNING") as logs:
            powersaver.perform_post_actions()

        self.assertEqual(completed, [True])
        self.assertEqual(len(logs.output), 1)
        self.assertIn("perform_post_action failed", logs.output[0])
        self.assertIn("Kodi is unavailable", logs.output[0])

    def test_pre_action_failure_is_logged_and_does_not_stop_later_actions(self):

        completed = []
        powersaver = PowerSaver.__new__(PowerSaver)
        powersaver._respite_prepare = 0
        powersaver._checkers = [
            FailingPreActionChecker({"preaction": True}),
            SuccessfulPreActionChecker(completed),
        ]
        wakeup = datetime(2026, 10, 11, 10, 0)

        with self.assertLogs(level="WARNING") as logs:
            powersaver.perform_pre_actions(wakeup)

        self.assertEqual(completed, [wakeup])
        self.assertEqual(len(logs.output), 1)
        self.assertIn("perform_pre_action failed", logs.output[0])
        self.assertIn("pre-action unavailable", logs.output[0])
