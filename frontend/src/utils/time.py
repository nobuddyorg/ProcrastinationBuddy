from datetime import datetime
import pytz


def format_time(dt, timezone):
    try:
        tz = pytz.timezone(timezone)
        dt_local = dt.astimezone(tz)
        now = datetime.now(tz)
    except Exception:
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    fmt = "%H:%M:%S" if dt_local.date() == now.date() else "%Y-%m-%d %H:%M:%S"
    return dt_local.strftime(fmt)
