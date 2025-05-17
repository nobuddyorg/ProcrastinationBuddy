from db.models import Task, AppSettings


def add_task_to_db(db, task_text: str):
    new_task = Task(task_text=task_text)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    subquery = db.query(Task.id).order_by(Task.created_at.desc()).limit(500).subquery()
    db.query(Task).filter(Task.id.not_in(subquery)).delete(synchronize_session=False)
    db.commit()


def like_task_in_db(db, task_id: int, like: int):
    task = db.query(Task).filter(Task.id == task_id).first()
    if task:
        task.favorite = like
        db.commit()
        db.refresh(task)
    return task


def get_tasks_from_db(db, skip=0, limit=10, favorite=None):
    query = db.query(Task).order_by(Task.created_at.desc())
    if favorite is not None:
        query = query.filter(Task.favorite == int(favorite))
    return query.offset(skip).limit(limit).all()


def count_tasks_in_db(db, favorite=None):
    query = db.query(Task)
    if favorite is not None:
        query = query.filter(Task.favorite == int(favorite))
    return query.count()


def delete_tasks_in_db(db, keep_favorites=False):
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
