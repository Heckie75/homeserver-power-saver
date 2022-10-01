from datetime import datetime

DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def format_datetime(dt: datetime) -> str:

    return dt.strftime("%Y-%m-%d %H:%M:%S")
