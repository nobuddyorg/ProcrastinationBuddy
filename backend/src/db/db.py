import os
import time
from collections.abc import Callable, Generator
from datetime import datetime, timezone

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    JSON,
)
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

# -----------------------#
# Configuration
# -----------------------#
DATABASE_URL = f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@{os.getenv('POSTGRES_HOST')}:{os.getenv('POSTGRES_PORT')}/{os.getenv('POSTGRES_DB')}"
DB_NAME_TASKS = "tasks"
DB_NAME_SETTINGS = "settings"
MAX_RETRIES = 120
RETRY_DELAY = 5
SQL_ECHO = os.getenv("SQL_ECHO", "false").lower() == "true"

Base = declarative_base()


# -----------------------#
# Database Engine Setup
# -----------------------#
def create_db_engine_with_retries(url: str, retries: int, delay: int) -> Engine:
    for attempt in range(retries):
        try:
            engine = create_engine(url, echo=SQL_ECHO)
            with engine.connect():
                pass
            return engine
        except OperationalError as e:
            print(f"Database connection failed (attempt {attempt + 1}/{retries}): {e}")
            time.sleep(delay)
    raise RuntimeError("Could not connect to the database after retries.")


# -----------------------#
# Utility
# -----------------------#
def utc_now() -> datetime:
    return datetime.now(timezone.utc)


# -----------------------#
# Models
# -----------------------#
class AppSettings(Base):
    __tablename__ = DB_NAME_SETTINGS

    id = Column(Integer, primary_key=True, index=True)
    settings = Column(JSON, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now)


class Task(Base):
    __tablename__ = DB_NAME_TASKS

    id = Column(Integer, primary_key=True, index=True)
    task_text = Column(String, nullable=False)
    favorite = Column(Integer, default=0)
    created_at = Column(DateTime, default=utc_now)


# -----------------------#
# Dependency
# -----------------------#
_engine = None
_Session = None


def init_db() -> None:
    global _engine, _Session
    if _engine is None:
        _engine = create_db_engine_with_retries(DATABASE_URL, MAX_RETRIES, RETRY_DELAY)
        _Session = sessionmaker(bind=_engine)
        Base.metadata.create_all(bind=_engine)


def get_db() -> Generator[Session, None, None]:
    if _Session is None:
        init_db()
    db = _Session()
    try:
        yield db
    finally:
        db.close()


def with_db_session(func: Callable) -> Callable:
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


# -----------------------#
# CRUD Operations
# -----------------------#
def add_task_to_db(db: Session, task_text: str) -> None:
    """Add a new task and keep only the latest 500 tasks in the DB."""
    new_task = Task(task_text=task_text)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    subquery = db.query(Task.id).order_by(Task.created_at.desc()).limit(500).subquery()
    db.query(Task).filter(Task.id.not_in(subquery.select())).delete(
        synchronize_session=False
    )
    db.commit()


def like_task_in_db(db: Session, task_id: int, like: int) -> Task | None:
    """Like or unlike a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.favorite = like
        db.commit()
        db.refresh(task)
    return task


def get_tasks_from_db(
    db: Session, skip: int = 0, limit: int = 10, favorite: bool | None = None
) -> list[Task]:
    query = db.query(Task).order_by(Task.created_at.desc())
    if favorite is not None:
        query = query.filter(Task.favorite == int(favorite))
    return query.offset(skip).limit(limit).all()


def count_tasks_in_db(db: Session, favorite: bool | None = None) -> int:
    query = db.query(Task)
    if favorite is not None:
        query = query.filter(Task.favorite == int(favorite))
    return query.count()


def delete_tasks_in_db(db: Session, keep_favorites: bool = True) -> int:
    query = db.query(Task)
    if keep_favorites:
        query = query.filter(Task.favorite == 0)
    deleted_count = query.delete()
    db.commit()
    return deleted_count


def get_app_settings_from_db(db: Session) -> AppSettings | None:
    return db.query(AppSettings).first()


def save_app_settings_to_db(db: Session, settings: dict) -> AppSettings:
    record = db.query(AppSettings).first()
    if record:
        record.settings = settings
    else:
        record = AppSettings(settings=settings)
        db.add(record)
    db.commit()
    db.refresh(record)
    return record
