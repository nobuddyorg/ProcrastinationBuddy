import time
from datetime import datetime, timezone

from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    String,
    DateTime,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

# -----------------------#
# Configuration
# -----------------------#
DATABASE_URL = "postgresql://taskuser:taskpass@procrastinationbuddy-db:5432/tasks"
DB_NAME_TASKS = "tasks"
DB_NAME_SETTINGS = "settings"
MAX_RETRIES = 120
RETRY_DELAY = 5


# -----------------------#
# Database Engine Setup
# -----------------------#
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


engine = create_db_engine_with_retries(DATABASE_URL, MAX_RETRIES, RETRY_DELAY)
Session = sessionmaker(bind=engine)
Base = declarative_base()


# -----------------------#
# Utility
# -----------------------#
def utc_now():
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


# Create tables if they don't exist
Base.metadata.create_all(bind=engine)


# -----------------------#
# Dependency
# -----------------------#
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


# -----------------------#
# CRUD Operations
# -----------------------#
def add_task_to_db(db, task_text: str):
    """Add a new task and keep only the latest 500 tasks in the DB."""
    new_task = Task(task_text=task_text)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    subquery = db.query(Task.id).order_by(Task.created_at.desc()).limit(500).subquery()
    db.query(Task).filter(Task.id.not_in(subquery)).delete(synchronize_session=False)
    db.commit()


def like_task_in_db(db, task_id: int, like: int):
    """Like or unlike a task."""
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.favorite = like
        db.commit()
        db.refresh(task)
    return task


def get_tasks_from_db(db, skip: int = 0, limit: int = 10, favorite: bool = None):
    query = db.query(Task).order_by(Task.created_at.desc())
    if favorite is not None:
        query = query.filter(Task.favorite == int(favorite))
    return query.offset(skip).limit(limit).all()


def count_tasks_in_db(db, favorite: bool = None):
    query = db.query(Task)
    if favorite is not None:
        query = query.filter(Task.favorite == int(favorite))
    return query.count()


def delete_tasks_in_db(db, keep_favorites: bool = False):
    query = db.query(Task)
    if keep_favorites:
        query = query.filter(Task.favorite == 0)
    deleted_count = query.delete()
    db.commit()
    return deleted_count


def get_app_settings_from_db(db):
    return db.query(AppSettings).first()


def save_app_settings_to_db(db, settings: dict):
    record = db.query(AppSettings).first()
    if record:
        record.settings = settings
    else:
        record = AppSettings(settings=settings)
        db.add(record)
    db.commit()
    db.refresh(record)
    return record
