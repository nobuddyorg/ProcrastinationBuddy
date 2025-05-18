import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.db import (
    Base,
    add_task_to_db,
    like_task_in_db,
    get_tasks_from_db,
    count_tasks_in_db,
    delete_tasks_in_db,
    save_app_settings_to_db,
    get_app_settings_from_db,
)

# -----------------------
# Pytest Fixtures
# -----------------------


@pytest.fixture
def in_memory_db():
    engine = create_engine("sqlite:///:memory:")
    TestingSession = sessionmaker(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSession()
    try:
        yield db
    finally:
        db.close()


# -----------------------
# Tests
# -----------------------


def test_add_and_count_tasks(in_memory_db):
    add_task_to_db(in_memory_db, "Test Task 1")
    add_task_to_db(in_memory_db, "Test Task 2")
    assert count_tasks_in_db(in_memory_db) == 2


def test_like_task(in_memory_db):
    add_task_to_db(in_memory_db, "Like me!")
    task = get_tasks_from_db(in_memory_db)[0]
    updated = like_task_in_db(in_memory_db, task.id, like=1)
    assert updated.favorite == 1


def test_get_tasks_filter_favorites(in_memory_db):
    add_task_to_db(in_memory_db, "Fav 1")
    add_task_to_db(in_memory_db, "Fav 2")
    task = get_tasks_from_db(in_memory_db)[0]
    like_task_in_db(in_memory_db, task.id, like=1)

    favs = get_tasks_from_db(in_memory_db, favorite=True)
    assert len(favs) == 1
    assert favs[0].favorite == 1


def test_delete_tasks_keep_favorites(in_memory_db):
    add_task_to_db(in_memory_db, "Task A")
    add_task_to_db(in_memory_db, "Task B")
    task = get_tasks_from_db(in_memory_db)[0]
    like_task_in_db(in_memory_db, task.id, like=1)

    deleted = delete_tasks_in_db(in_memory_db, keep_favorites=True)
    assert deleted == 1
    assert count_tasks_in_db(in_memory_db) == 1


def test_app_settings_crud(in_memory_db):
    settings_data = {"theme": "dark"}
    saved = save_app_settings_to_db(in_memory_db, settings_data)
    assert saved.settings["theme"] == "dark"

    new_settings = {"theme": "light"}
    save_app_settings_to_db(in_memory_db, new_settings)
    fetched = get_app_settings_from_db(in_memory_db)
    assert fetched.settings["theme"] == "light"
