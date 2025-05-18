from datetime import datetime, timedelta
from utils.time import format_time
import pytz
from unittest.mock import patch


def test_format_time_same_day():
    utc = pytz.UTC
    fixed_now = datetime(2025, 5, 18, 12, 0, 0, tzinfo=utc)
    test_time = fixed_now.replace(hour=10, minute=30)

    with patch("utils.time.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_now
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        result = format_time(test_time, "UTC")

    assert result == "10:30:00"


def test_format_time_different_day():
    utc = pytz.UTC
    fixed_now = datetime(2025, 5, 18, 12, 0, 0, tzinfo=utc)
    test_time = fixed_now - timedelta(days=1)

    with patch("utils.time.datetime") as mock_datetime:
        mock_datetime.now.return_value = fixed_now
        mock_datetime.side_effect = lambda *args, **kwargs: datetime(*args, **kwargs)
        result = format_time(test_time, "UTC")

    assert result == (test_time).strftime("%Y-%m-%d %H:%M:%S")


def test_format_time_invalid_timezone():
    dt = datetime(2024, 1, 1, 12, 30, 0)
    result = format_time(dt, "Invalid/Zone")
    assert result == "2024-01-01 12:30:00"
