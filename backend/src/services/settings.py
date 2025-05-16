from src.db.db import with_db_session, get_app_settings_from_db, save_app_settings_to_db


@with_db_session
def get_settings(db):
    return get_app_settings_from_db(db)


@with_db_session
def save_settings(db, settings):
    return save_app_settings_to_db(db, settings)
