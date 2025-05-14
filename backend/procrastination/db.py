import time
from datetime import datetime, timezone
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import OperationalError

DATABASE_URL = "postgresql://taskuser:taskpass@pb-db:5432/tasks"
DB_NAME = "tasks"

MAX_RETRIES = 120
RETRY_DELAY = 5

for attempt in range(MAX_RETRIES):
    try:
        engine = create_engine(DATABASE_URL, echo=True)
        with engine.connect() as connection:
            pass
        Session = sessionmaker(bind=engine)
        break
    except OperationalError as e:
        print(f"Database connection failed (attempt {attempt + 1}/{MAX_RETRIES}): {e}")
        time.sleep(RETRY_DELAY)
else:
    raise RuntimeError("Could not connect to the database after 60 seconds.")

Base = declarative_base()


class Task(Base):
    __tablename__ = DB_NAME

    id = Column(Integer, primary_key=True, index=True)
    task_text = Column(String, nullable=False)
    favorite = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


Base.metadata.create_all(bind=engine)


def get_db():
    db = Session()
    try:
        yield db
    finally:
        db.close()


def add_task_to_db(db, task_text: str):
    """Add a new task and keep only the latest 100 tasks in the DB."""
    new_task = Task(task_text=task_text, favorite=0)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    subquery = db.query(Task.id).order_by(Task.created_at.desc()).limit(100).subquery()
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
    return None


def get_tasks_from_db(db, skip: int = 0, limit: int = 10, favorite=None):
    query = db.query(Task).order_by(Task.created_at.desc())
    if favorite is not None:
        favorite_value = 1 if favorite else 0
        query = query.filter(Task.favorite == favorite_value)

    query = query.offset(skip).limit(limit)

    return query.all()


def count_tasks_in_db(db, favorite=None):
    query = db.query(Task)
    if favorite is not None:
        query = query.filter(Task.favorite == (1 if favorite else 0))
    return query.count()


def delete_tasks_in_db(db, keep_favorites=False):
    query = db.query(Task)
    if keep_favorites:
        query = query.filter(Task.favorite == 0)

    deleted_count = query.delete()
    db.commit()
    return deleted_count
