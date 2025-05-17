from db.config import (
    DATABASE_URL,
    create_db_engine_with_retries,
    MAX_RETRIES,
    RETRY_DELAY,
)
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, timezone

engine = create_db_engine_with_retries(DATABASE_URL, MAX_RETRIES, RETRY_DELAY)
Base = declarative_base()
Base.metadata.create_all(bind=engine)


def utc_now():
    return datetime.now(timezone.utc)
