import json
import logging
import os
import re
from datetime import datetime, timedelta

import requests

from checkers.abstractinterruptionchecker import AbstractInterruptionChecker

LOGGER = logging.getLogger()


class KodiJsonRpcClient():

    def __init__(self, host, port, user, password) -> None:

        self._host = host
        self._port = port
        self._user = user
        self._password = password

    def _request(self, payload) -> 'dict':

        try:
            response = requests.request("POST", "http://%s:%i/jsonrpc" % (
                self._host, self._port), auth=(self._user, self._password) if self._user and self._password else None, data=json.dumps(payload))

            if response.ok:
                LOGGER.debug(response.text)
                return json.loads(response.text)

            else:
                LOGGER.error(
                    "Kodi has responded with HTTP status code %i" % response.status_code)
                return None
        except:
            LOGGER.error("Unexpected error", exc_info=True)
            return None

    def set_volume(self, volume: int) -> None:

        payload = [
            {"jsonrpc": "2.0", "method": "Application.SetVolume", "id": 1, "params": {"volume": volume}}]
        self._request(payload=payload)


class KodiTimersInterruptionChecker(AbstractInterruptionChecker):

    MEDIA_ACTION_START_STOP = 1
    MEDIA_ACTION_START = 2
    MEDIA_ACTION_START_AT_END = 3
    MEDIA_ACTION_STOP_START = 4

    TIMER_WEEKLY = 7
    TIMER_BY_DATE = 8

    TIMERS_PATH = "userdata/addon_data/script.timers/timers.json"
    SETTINGS_PATH = "userdata/addon_data/script.timers/settings.xml"

    def __init__(self, setting) -> None:

        super().__init__(setting)
        self._timers_file: str = os.path.join(
            setting["path"], self.TIMERS_PATH)
        self._settings_file: str = os.path.join(
            setting["path"], self.SETTINGS_PATH)

        if "postaction" in setting and setting["postaction"]:
            self._kodiJsonRpcClient = KodiJsonRpcClient(
                setting["host"], setting["port"], setting["user"], setting["password"])
        else:
            self._kodiJsonRpcClient = None

    def _load_file(self, path: str) -> str:

        with open(path, "r") as f:
            s = "\n".join(f.readlines())
            f.close()

        return s

    def _load_timers_json(self):

        return self._load_file(self._timers_file)

    def _load_settings_xml(self):

        return self._load_file(self._settings_file)

    def _get_settings(self, timers_settings_xml: str) -> 'tuple[datetime, datetime, int, int]':

        def parse_datetime(s: str) -> datetime:

            return datetime.strptime(s, "%Y-%m-%d %H:%M:%S")

        def parse_value(s: str) -> str:

            m = re.match("^.*<setting[^>]+>([^<]+)<\/setting>.*$", s)
            return m.groups()[0] if m else None

        pause_date_from = None
        pause_time_from = None
        pause_date_until = None
        pause_time_until = None
        offset = 0
        vol_default = 100

        for l in timers_settings_xml.splitlines():
            if "id=\"pause_date_from\"" in l:
                pause_date_from = parse_value(l)

            elif "id=\"pause_time_from\"" in l:
                pause_time_from = parse_value(l)

            elif "id=\"pause_date_until\"" in l:
                pause_date_until = parse_value(l)

            elif "id=\"pause_time_until\"" in l:
                pause_time_until = parse_value(l)

            elif "id=\"offset\"" in l:
                offset = int(parse_value(l))

            elif "id=\"vol_default\"" in l:
                vol_default = int(parse_value(l))

            else:
                pass

        return parse_datetime("%s %s:00" % (pause_date_from, pause_time_from)), parse_datetime("%s %s:00" % (pause_date_until, pause_time_until)), offset, vol_default

    def _get_media_actions(self, timers: dict, dt_now: datetime) -> 'list[datetime]':

        def apply_for_now(dt_now: datetime, timestamp: timedelta) -> datetime:

            dt_last_monday_same_time = dt_now - \
                timedelta(days=dt_now.weekday())
            dt_last_monday_midnight = datetime(year=dt_last_monday_same_time.year,
                                               month=dt_last_monday_same_time.month,
                                               day=dt_last_monday_same_time.day)

            return dt_last_monday_midnight + timestamp

        td_now = timedelta(days=dt_now.weekday(),
                           hours=dt_now.hour, minutes=dt_now.minute)

        actions = list()
        for t in timers:

            if t["path"] and t["media_action"] in [self.MEDIA_ACTION_START_STOP, self.MEDIA_ACTION_START]:
                _ts: str = t["start"]
                _offset = t["start_offset"]
                _next_day = 0

            elif t["path"] and t["media_action"] in [self.MEDIA_ACTION_STOP_START, self.MEDIA_ACTION_START_AT_END]:
                _ts: str = t["end"]
                _offset = t["end_offset"]
                _next_day = 0 if t["start"] <= t["end"] else 1

            else:
                continue

            for d in t["days"]:
                if d == self.TIMER_WEEKLY:
                    continue

                elif d == self.TIMER_BY_DATE:
                    actions.append(datetime.strptime("%s %s" %
                                   (t["date"], _ts), "%Y-%m-%d %H:%M"))

                else:
                    _hh_mm = _ts.split(":")
                    td_media_action = timedelta(days=(d + _next_day) %
                                                7, hours=int(_hh_mm[0]), minutes=int(_hh_mm[1]), seconds=_offset)

                    if td_media_action < td_now:
                        if self.TIMER_WEEKLY in t["days"]:
                            td_media_action += timedelta(days=7)
                        else:
                            continue

                    actions.append(apply_for_now(dt_now, td_media_action))

        return actions

    def get_upcoming_event(self, dt_now: datetime) -> datetime:

        pause_from, pause_to, offset, vol_default = self._get_settings(
            self._load_settings_xml())
        timers = json.loads(self._load_timers_json())
        actions = self._get_media_actions(timers, dt_now)
        if pause_to and pause_to > dt_now:
            actions.extend(self._get_media_actions(timers, pause_to))

        closest_event = None
        for action in actions:
            if pause_from and pause_to and pause_from <= action < pause_to:
                continue

            elif not closest_event or action < closest_event:
                closest_event = action

        return closest_event + timedelta(seconds=offset) if closest_event else None

    def perform_post_action(self) -> None:

        pause_from, pause_to, offset, vol_default = self._get_settings(
            self._load_settings_xml())
        self._kodiJsonRpcClient.set_volume(vol_default)
