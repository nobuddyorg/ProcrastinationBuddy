from sqlalchemy.orm import sessionmaker
from db.config import (
    DATABASE_URL,
    create_db_engine_with_retries,
    MAX_RETRIES,
    RETRY_DELAY,
)

engine = create_db_engine_with_retries(DATABASE_URL, MAX_RETRIES, RETRY_DELAY)
Session = sessionmaker(bind=engine)


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


def with_db_session(func):
    def wrapper(*args, **kwargs):
        db_gen = get_db()
        db = next(db_gen)
        try:
            return func(db, *args, **kwargs)
        finally:
            try:
                next(db_gen)
            except StopIteration:
                pass

    return wrapper
