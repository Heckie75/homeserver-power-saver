from datetime import datetime, timedelta

from utils.periods import Periods

import logging
LOGGER = logging.getLogger()


class AbstractInterruptionChecker():

    def __init__(self, setting) -> None:

        self.setting = setting
        self.stay_awake = timedelta(
            minutes=setting["stay_awake"]) if setting and "stay_awake" in setting else timedelta()
        self.extra_wakeup_time = timedelta(
            minutes=setting["extra_wakeup_time"]) if setting and "extra_wakeup_time" in setting else timedelta()
        self.pre_action = setting["preaction"] if setting and "preaction" in setting else False
        self.post_action = setting["postaction"] if setting and "postaction" in setting else False

        self.ignore_periods = Periods()
        if setting and "ignore_periods" in setting:
            self.ignore_periods.append_from_settings(setting["ignore_periods"])

    def _get_occupation(self, dt_now: datetime) -> timedelta:

        _running, _period = self.ignore_periods.get_next_period(dt_now)
        if _running:
            LOGGER.info("%s: Skip since check is in ignored period." %
                        self.__class__.__name__)
            return None

        try:
            return self.get_occupation(dt_now)

        except:
            LOGGER.error("%s: check_occupation" %
                         self.__class__.__name__, exc_info=True)
            return None

    def get_occupation(self, dt_now: datetime) -> timedelta:

        return None

    def _get_upcoming_event(self, dt_now: datetime) -> datetime:

        try:
            event = self.get_upcoming_event(dt_now)
            if event:
                return dt_now if event - self.extra_wakeup_time < dt_now < event else event - self.extra_wakeup_time
            else:
                return None

        except:
            LOGGER.error("%s: get_upcoming_event" %
                         self.__class__.__name__, exc_info=True)
            return None

    def get_upcoming_event(self, dt_now: datetime) -> datetime:

        return None

    def _perform_pre_action(self, dt_wakeup: datetime) -> None:

        if self.pre_action:
            self.perform_pre_action(dt_wakeup)

    def _perform_post_action(self) -> None:

        if self.post_action:
            self.perform_post_action()

    def perform_pre_action(self, dt_wakeup: datetime) -> None:

        pass

    def perform_post_action(self) -> None:

        pass
