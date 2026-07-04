from sqlalchemy.orm import Session
from db.db import with_db_session, get_app_settings_from_db, save_app_settings_to_db
from db.db import AppSettings


@with_db_session
def get_settings(db: Session) -> AppSettings | None:
    return get_app_settings_from_db(db)


@with_db_session
def save_settings(db: Session, settings: dict) -> AppSettings:
    return save_app_settings_to_db(db, settings)
