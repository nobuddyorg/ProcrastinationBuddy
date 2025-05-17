import time
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError

DATABASE_URL = "postgresql://taskuser:taskpass@procrastinationbuddy-db:5432/tasks"
MAX_RETRIES = 120
RETRY_DELAY = 5


def create_db_engine_with_retries(url: str, retries: int, delay: int):
    for attempt in range(retries):
        try:
            engine = create_engine(url, echo=True)
            with engine.connect():
                pass
            return engine
        except OperationalError as e:
            print(f"Database connection failed (attempt {attempt + 1}/{retries}): {e}")
            time.sleep(delay)
    raise RuntimeError("Could not connect to the database after retries.")
