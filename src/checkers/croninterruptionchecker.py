import logging
import re
from datetime import datetime, timedelta
from sys import platform

from checkers.abstractinterruptionchecker import \
    AbstractInterruptionChecker

try:
    from crontab import CronItem, CronTab
except ImportError:
    CronTab = None

LOGGER = logging.getLogger()


class CronInterruptionChecker(AbstractInterruptionChecker):

    _ANNOTATION_PATTERN = r"@homeserver-power-saver\(([^\)]+)\)"

    def __init__(self, setting) -> None:
        super().__init__(setting)

        if "ignore_frequency" in setting:
            self._max_per_year = setting["ignore_frequency"][
                "max_per_year"] if "max_per_year" in setting["ignore_frequency"] else None
            self._max_days_per_year = setting["ignore_frequency"][
                "max_days_per_year"] if "max_days_per_year" in setting["ignore_frequency"] else None
            self._max_per_day = setting["ignore_frequency"]["max_per_day"] if "max_per_day" in setting["ignore_frequency"] else None
            self._max_per_hour = setting["ignore_frequency"][
                "max_per_hour"] if "max_per_hour" in setting["ignore_frequency"] else None

    def _get_crontabs(self) -> 'list[CronTab]':

        if not platform.startswith("linux"):
            return list()

        crontabs = list()
        if "users" in self.setting and self.setting["users"]:
            for user in self.setting["users"]:
                try:
                    crontabs.append(CronTab(user=user))
                except:
                    LOGGER.error("Error while reading crontabs for user %s. Do you have permission?" % user, exc_info=True)

        if "tabfiles" in self.setting and self.setting["tabfiles"]:
            for tabfile in self.setting["tabfiles"]:
                try:
                    crontabs.append(CronTab(tabfile=tabfile))
                except:
                    LOGGER.error("Error while reading crontab from tabfile %s. Do you have permission?" % tabfile, exc_info=True)

        return crontabs

    def _parse_annotation(self, cronitem: 'CronItem') -> 'tuple[bool,bool,timedelta,timedelta]':

        ignore = False
        force = False
        stay_awake = timedelta()
        extra_wakeup_time = timedelta()

        comment = cronitem.comment
        m = re.match(self._ANNOTATION_PATTERN, comment)
        if not m:
            return ignore, force, stay_awake, extra_wakeup_time

        try:
            if m.groups()[0]:
                LOGGER.debug("Cron job is annotated: %s" % m.groups()[0])

                for param in m.groups()[0].split(","):
                    kv = param.split("=")
                    key = kv[0].strip()
                    value = kv[1].strip()

                    if key == "ignore":
                        ignore = "true" == value
                    elif key == "force":
                        force = "true" == value
                    elif key == "stay_awake":
                        stay_awake = timedelta(minutes=int(value))
                    elif key == "extra_wakeup_time":
                        extra_wakeup_time = timedelta(minutes=int(value))

                return ignore, force, stay_awake, extra_wakeup_time

        except:
            LOGGER.error("Can't parse annotation from comment %s" % comment, exc_info=True)
            return ignore, force, stay_awake, extra_wakeup_time

    def _get_schedule(self, cronitem: 'CronItem', dt_now: datetime) -> 'tuple[datetime,datetime]':

        if not cronitem.is_valid() or not cronitem.is_enabled():
            return None, None

        ignore, force, stay_awake, extra_wakeup_time = self._parse_annotation(
            cronitem=cronitem)

        if ignore:
            return None, None

        elif not force:
            if self._max_per_year and cronitem.frequency() > self._max_per_year:
                return None, None

            elif self._max_days_per_year and cronitem.frequency_per_year() > self._max_days_per_year:
                return None, None

            elif self._max_per_day and cronitem.frequency_per_day() > self._max_per_day:
                return None, None

            elif self._max_per_hour and cronitem.frequency_per_hour() > self._max_per_hour:
                return None, None

        schedule = cronitem.schedule(date_from=dt_now)
        dt_prev: datetime = schedule.get_prev()
        dt_next: datetime = schedule.get_next()

        dt_eta = dt_prev + (stay_awake or self.stay_awake)
        dt_schedule = dt_next - extra_wakeup_time + \
            (self.extra_wakeup_time if extra_wakeup_time else timedelta())

        return dt_eta, dt_schedule

    def get_occupation(self, dt_now: datetime) -> timedelta:

        dt_latest_eta = None
        for cron in self._get_crontabs():
            for item in cron:
                dt_eta, dt_schedule = self._get_schedule(
                    cronitem=item, dt_now=dt_now)
                dt_latest_eta = dt_eta if dt_eta and (
                    dt_latest_eta is None or dt_eta > dt_latest_eta) else dt_latest_eta

        if dt_latest_eta and dt_latest_eta > dt_now:
            stay_awake = dt_latest_eta - dt_now
            return stay_awake

        else:
            return None

    def get_upcoming_event(self, dt_now: datetime) -> datetime:

        closest_event = None
        for cron in self._get_crontabs():
            for item in cron:
                dt_eta, dt_schedule = self._get_schedule(
                    cronitem=item, dt_now=dt_now)

                closest_event = dt_schedule if not closest_event or (
                    dt_schedule and dt_schedule < closest_event) else closest_event

        return closest_event
