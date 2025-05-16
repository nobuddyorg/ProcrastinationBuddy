import requests
from src.db.db import (
    get_db,
    add_task_to_db,
    get_tasks_from_db,
    like_task_in_db,
    count_tasks_in_db,
    delete_tasks_in_db,
)


def ensure_model_exists(url, model):
    tags_response = requests.get(f"{url}/api/tags")
    tags_response.raise_for_status()
    models = [m["name"] for m in tags_response.json().get("models", [])]
    if model not in models:
        pull_response = requests.post(f"{url}/api/pull", json={"name": model})
        pull_response.raise_for_status()


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
def generate_task(db, url, language, model):
    ensure_model_exists(url, model)
    response = requests.post(
        f"{url}/api/generate",
        json={
            "model": model,
            "prompt": generate_prompt(language),
            "stream": False,
            "temperature": 0.9,
        },
    )
    response.raise_for_status()
    task_text = response.json()["response"].strip()
    add_task_to_db(db, task_text)
    return task_text


def generate_prompt(language):
    examples = [
        "watch baby animal videos on Youtube",
        "Count the number of tiles in the bathroom",
        "Organize your pens by color and size",
        "Reversing all your stacks of plates and bowls to ensure even wear",
        "Write a poem about the dust bunnies under your bed",
    ]
    return f"""You are 'Procrastination Buddy', a creative assistant for generating procrastination tasks.

Generate ONE procrastination task that:
- Is short.
- Can be casual or elaborate, but must be fun.
- Avoids giving explanations, reasons.
- Language (no translations): {language}

Examples of my favorites: {", ".join(examples)}

Respond only with the task itself.
"""


@with_db_session
def like_task(db, task_id, like):
    like_task_in_db(db, task_id, like)


@with_db_session
def list_tasks(db, skip=0, limit=10, favorite=None):
    tasks = get_tasks_from_db(
        db,
        skip=skip,
        limit=limit,
        favorite=bool(favorite) if favorite is not None else None,
    )
    return [
        {
            "id": t.id,
            "task_text": t.task_text,
            "created_at": t.created_at,
            "favorite": t.favorite,
        }
        for t in tasks
    ]


@with_db_session
def count_tasks(db, favorite=None):
    return count_tasks_in_db(db, favorite=favorite)


@with_db_session
def delete_all_tasks(db, keep_favorites=True):
    delete_tasks_in_db(db, keep_favorites=keep_favorites)
