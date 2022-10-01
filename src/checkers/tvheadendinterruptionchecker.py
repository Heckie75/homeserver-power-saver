import json
import logging
from datetime import datetime, timedelta

import requests
from requests.auth import HTTPDigestAuth

from checkers.abstractinterruptionchecker import \
    AbstractInterruptionChecker

LOGGER = logging.getLogger()


class TvHeadendHttpClient():

    def __init__(self, host, port, user, password) -> None:

        self._host = host
        self._port = port
        self._user = user
        self._password = password

    def _request(self, request) -> 'dict':

        try:
            response = requests.request("POST", "http://%s:%i/api/%s" % (
                self._host, self._port, request), auth=HTTPDigestAuth(self._user, self._password) if self._user and self._password else None)

            if response.ok:
                return json.loads(response.text)

            else:
                LOGGER.error("TVHeadend has responded with HTTP status code %i" % response.status_code)
                return None
        except:
            LOGGER.error("Unexpected error", exc_info=True)
            return None

    def get_subscriptions(self) -> None:

        response = self._request("status/subscriptions")
        if response:
            LOGGER.debug("Subscriptions %s" %
                         json.dumps(response, indent=2))
        return response

    def get_upcoming_recordings(self) -> None:

        response = self._request("dvr/entry/grid_upcoming")
        if response:
            LOGGER.debug("Recordings %s" %
                         json.dumps(response, indent=2))
        return response


class TvHeadendInterruptionChecker(AbstractInterruptionChecker):

    def __init__(self, setting) -> None:

        super().__init__(setting)
        self._tvHeadendHttpClient = TvHeadendHttpClient(
            setting["host"], setting["port"], setting["user"], setting["password"])

    def _has_subscriptions(self) -> bool:

        subscriptions = self._tvHeadendHttpClient.get_subscriptions()
        if subscriptions is not None:
            return subscriptions["totalCount"] > 0

        return False

    def _get_recording_starting_times(self) -> 'list[datetime]':

        _recordings = self._tvHeadendHttpClient.get_upcoming_recordings()
        if not _recordings or "entries" not in _recordings:
            return list()

        return [datetime.fromtimestamp(r["start_real"]) for r in _recordings["entries"] if r["enabled"]]

    def get_occupation(self, dt_now: datetime) -> timedelta:

        return self.stay_awake if self._has_subscriptions() else None

    def get_upcoming_event(self, dt_now: datetime) -> datetime:

        closest_event = None
        for start in self._get_recording_starting_times():
            if dt_now <= start and (closest_event is None or start < closest_event):
                closest_event = start

        return closest_event
