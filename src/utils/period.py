from datetime import datetime, timedelta

from utils.datetimeutils import DAYS, format_datetime


class Period():

    def __init__(self, start: timedelta, end: timedelta) -> None:

        self.start = start
        self.end = end

    def _format_timedelta(self, td: timedelta) -> str:

        if td.days > 7:
            return format_datetime(datetime.fromtimestamp(td.total_seconds()))

        else:
            return "%s %02i:%02i" % (DAYS[td.days % 7], td.seconds // 3600, td.seconds % 3600 // 60)

    def _overlap(self, period_start: timedelta, period_end: timedelta) -> 'tuple[timedelta,timedelta]':

        self_start = self.start
        self_end = self.end
        week = timedelta(days=7)

        if self_start > self_end and period_start <= period_end:
            self_end += week
            if period_end < self_start:
                period_start += week
                period_end += week

        elif self_start <= self_end and period_start > period_end:
            period_end += week
            if self_end < period_start:
                self_start += week
                self_end += week

        if self_start <= period_start <= self_end \
                or self_start <= period_end <= self_end \
                or period_start <= self_start <= period_end \
                or period_start <= self_end <= period_end \
                or self_start > self_end and period_start > period_end:

            return self_start - period_start, self_end - period_end
        else:
            return None, None

    def overlap(self, period: 'Period') -> 'tuple[timedelta,timedelta]':

        return self._overlap(period_start=period.start, period_end=period.end)

    def hit(self, timestamp: timedelta) -> 'tuple[timedelta,timedelta]':

        return self._overlap(period_start=timestamp, period_end=timestamp)

    def apply_for_this_week(self, dt_now=None) -> 'Period':

        if not dt_now:
            dt_now = datetime.today()

        dt_last_monday_same_time = dt_now - timedelta(days=dt_now.weekday())
        dt_last_monday_midnight = datetime(year=dt_last_monday_same_time.year,
                                           month=dt_last_monday_same_time.month,
                                           day=dt_last_monday_same_time.day)
        td_start = timedelta(
            seconds=(dt_last_monday_midnight + self.start).timestamp())
        td_end = timedelta(
            seconds=(dt_last_monday_midnight + self.end).timestamp())

        if td_start > td_end:
            if td_end.total_seconds() > dt_now.timestamp():
                td_start -= timedelta(days=7)
            else:
                td_end += timedelta(days=7)

        return Period(td_start, td_end)

    def __str__(self) -> str:

        return "%s -> %s" % (self._format_timedelta(self.start), self._format_timedelta(self.end))
