from datetime import datetime, timedelta
from utils.period import Period

class Periods():

    def __init__(self) -> None:

        self.periods: 'list[Period]' = list()

    def append_from_settings(self, settings: list) -> None:

        for _rt in settings:
            _start = [int(v) for v in _rt["from"].split(":")]
            _end = [int(v) for v in _rt["until"].split(":")]
            for _d in _rt["days"]:
                td_start_time = timedelta(hours=_start[0], minutes=_start[1])
                td_end_time = timedelta(hours=_end[0], minutes=_end[1])

                td_end = td_end_time + \
                    timedelta(
                        days=(_d + (1 if td_start_time >= td_end_time else 0)) % 7)
                td_start = td_start_time + timedelta(days=_d)
                self.add(Period(td_start, td_end))

        self.unify()

    def add(self, Period) -> None:

        self.periods.append(Period)

    def unify(self) -> None:

        def _unify_periods(periods: 'list[Period]') -> bool:

            l = len(periods)
            if l < 2:
                return False

            for i in range(l - 1):

                td_dist_start, td_dist_end = periods[i].overlap(periods[i+1])
                if td_dist_start:
                    joined_start = periods[i].start if td_dist_start <= timedelta(
                        0) else periods[i+1].start
                    joined_end = periods[i].end if td_dist_end > timedelta(
                        0) else periods[i+1].end
                    periods[i] = Period(joined_start, joined_end)
                    periods.pop(i+1)
                    return True

            return False

        self.periods.sort(key=lambda p: p.start)

        while _unify_periods(self.periods):
            pass

    def get_next_period(self, dt_now: datetime) -> 'tuple[bool, Period]':

        td_now = timedelta(hours=dt_now.hour, minutes=dt_now.minute,
                           seconds=dt_now.second, days=dt_now.weekday())
        next = timedelta.max
        next_period = None

        for p in self.periods:
            td_start, td_end = p.hit(td_now)
            if td_start is not None:
                return True, p.apply_for_this_week(dt_now)

            elif p.start > td_now and next > p.start - td_now:
                next = p.start - td_now
                next_period = p

            elif p.start < td_now and next > timedelta(days=7) + p.start - td_now:
                next = timedelta(days=7) + p.start - td_now
                next_period = p

        return False, next_period.apply_for_this_week(dt_now) if next_period else None

    def __str__(self) -> str:

        s = ""
        for p in self.periods:
            s += "%s\n" % str(p)

        return s