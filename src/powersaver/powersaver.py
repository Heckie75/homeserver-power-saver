#!/usr/bin/python3
import logging
import subprocess
import time
from datetime import datetime, timedelta
from pydoc import locate

from checkers.abstractinterruptionchecker import \
    AbstractInterruptionChecker
from utils.datetimeutils import format_datetime

LOGGER = logging.getLogger()


class PowerSaver():

    def __init__(self, settings):

        if not settings:
            return

        self._td_min_uptime = timedelta(
            minutes=settings["min_uptime"] if "min_uptime" in settings else 0)
        self._td_min_downtime = timedelta(
            minutes=settings["min_downtime"] if "min_downtime" in settings else 0)

        self._respite_prepare: int = settings["respite_prepare"]
        self._respite_recover: int = settings["respite_recover"]

        self._mode: str = settings["mode"]
        self._dryrun: bool = settings["dryrun"]

        self._checkers: 'list[AbstractInterruptionChecker]' = list()
        for c in settings["checkers"]:
            if not c.endswith("InterruptionChecker") or "enable" not in settings["checkers"][c] or not settings["checkers"][c]["enable"]:
                continue

            LOGGER.info("Initialising %s" % c)
            class_ = locate("checkers.%s.%s" % (c.lower(), c))
            self._checkers.append(class_(settings["checkers"][c]))

    def perform_pre_actions(self, dt_wakeup: datetime = None) -> None:

        LOGGER.debug("perform pre-actions ...")

        for c in self._checkers:
            LOGGER.debug("perform pre-action for %s" % c.__class__.__name__)
            c._perform_pre_action(dt_wakeup)

        time.sleep(self._respite_prepare)

    def perform_post_actions(self) -> None:

        LOGGER.debug("perform post-actions ...")

        time.sleep(self._respite_recover)

        for i in range(len(self._checkers), 0, -1):
            LOGGER.debug("perform post-action for %s" %
                         self._checkers[i - 1].__class__.__name__)
            self._checkers[i - 1]._perform_post_action()

    def _shutdown(self) -> None:

        args = list(["shutdown", "now"])
        LOGGER.debug("Execute shutdown: %s" % " ".join(args))
        subprocess.call(args)
        exit(0)

    def _rtcwake(self, rest_until: datetime) -> None:

        args = list(["rtcwake"])
        if self._dryrun:
            args.append("-n")

        args.extend(["-m", self._mode,
                    "--date", format_datetime(rest_until)])

        LOGGER.debug("Execute rtcwake: %s" % " ".join(args))
        subprocess.call(args)

    def reset_wakealarm(self) -> None:

        LOGGER.debug("reset wake alarm in rtc0")

        with open("/sys/class/rtc/rtc0/wakealarm", "w") as f:
            f.write(str(0))

    def set_wakealarm(self, wake_alarm: datetime) -> None:

        ts = int(wake_alarm.timestamp())

        LOGGER.debug("set wake alarm directly on device rtc0: %s (%i)" % (format_datetime(wake_alarm), ts))

        with open("/sys/class/rtc/rtc0/wakealarm", "w") as f:
            f.write(str(ts))

    def _perform_rest_procedure(self, dt_wakeup: datetime) -> None:

        # perform pre-actions of checkers
        self.perform_pre_actions(dt_wakeup)

        if self._mode == "shutdown":
            # shutdown system
            LOGGER.info("Shutdown system. Bye bye!")
            self._shutdown()

        else:
            # perform rtcwake that suspends system
            LOGGER.info("Make a rest until %s. See you later!" %
                        format_datetime(dt_wakeup))
            self._rtcwake(dt_wakeup)

        LOGGER.info("Waking up...")

        # perform post-actions of checkers
        self.perform_post_actions()

    def _get_occupation(self, dt_now: datetime) -> timedelta:

        # check if device is busy
        busy = timedelta()
        for c in self._checkers:
            _busy = c._get_occupation(dt_now)
            if _busy is not None:
                LOGGER.info("%s: Request to keep device up for %i minutes." % (
                    c.__class__.__name__, _busy.total_seconds() // 60))
                busy = _busy if busy < _busy else busy

        # If PC is busy then don't enter rest period
        if busy:
            dt_busy_until = dt_now + busy
            return dt_busy_until

        else:
            return None

    def get_upcoming_event(self, dt_now: datetime) -> datetime:

        closest_event = None
        for c in self._checkers:

            next_event = c._get_upcoming_event(dt_now)
            if not next_event or next_event < dt_now:
                continue

            closest_event = next_event if not closest_event or next_event < closest_event else closest_event

        return closest_event

    def main(self) -> None:

        try:
            dt_busy_until = None

            LOGGER.debug("Main loop for checker started.")
            while True:

                time.sleep(60 - int(time.time() % 60))
                dt_now = datetime.today()

                _busy = self._get_occupation(dt_now)
                if _busy and (not dt_busy_until or dt_busy_until < _busy):
                    dt_busy_until = _busy
                    LOGGER.info(
                        "Can't go to rest since PC is busy. Keep PC awake at least until %s" % format_datetime(dt_busy_until))

                elif dt_busy_until and dt_busy_until > dt_now:
                    LOGGER.debug(
                        "Device was busy and asked to stay awake at least until %s" % format_datetime(dt_busy_until))

                else:
                    upcoming_event = self.get_upcoming_event(dt_now)
                    if upcoming_event and upcoming_event - dt_now > self._td_min_downtime:
                        self._perform_rest_procedure(upcoming_event)

                        dt_busy_until = datetime.today() + self._td_min_uptime
                        LOGGER.info(
                            "PC has been woken up. Keep PC awake at least until %s." % format_datetime(dt_busy_until))

                    else:
                        # prevent that device is going to rest for a short period
                        dt_busy_until = dt_now + self._td_min_downtime
                        LOGGER.info("Won't go to rest since rest time would be shorter than %i minutes." % (
                            self._td_min_downtime.total_seconds() // 60))

        except (KeyboardInterrupt, SystemExit):
            LOGGER.info(
                "homeserver-power-saver interrupted by KeyboardInterrupt or SystemExit")

        except Exception as ex:
            LOGGER.error("%s: %s" % (type(ex), ex), exc_info=True)

        finally:
            LOGGER.info("homeserver-power-saver terminated")
