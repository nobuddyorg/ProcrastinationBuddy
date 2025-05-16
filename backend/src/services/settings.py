from src.db.db import get_db, get_app_settings_from_db, save_app_settings_to_db


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


@with_db_session
def get_settings(db):
    return get_app_settings_from_db(db)


@with_db_session
def save_settings(db, settings):
    return save_app_settings_to_db(db, settings)
