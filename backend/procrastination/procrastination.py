import requests
from .db import get_db, add_task_to_db, get_tasks_from_db, like_task_in_db


def ensure_model_exists(url, model):
    """Ensure the model is available in Ollama. Pull it if not."""
    tags_response = requests.get(f"{url}/api/tags")
    tags_response.raise_for_status()
    models = [m["name"] for m in tags_response.json().get("models", [])]

    if model not in models:
        pull_response = requests.post(f"{url}/api/pull", json={"name": model})
        pull_response.raise_for_status()


def procrastinate(url, language, model):
    ensure_model_exists(url, model)
    url = f"{url}/api/generate"

    favorites = [
        "watch baby animal videos on Youtube",
        "Count the number of tiles in the bathroom",
        "Organize your pens by color and size",
        "Reversing all your stacks of plates and bowls to ensure even wear",
        "Write a poem about the dust bunnies under your bed",
    ]

    prompt = f"""You are 'Procrastination Buddy', a creative assistant for generating procrastination tasks.

Generate ONE procrastination task that:
- Is short.
- Can be casual or elaborate, but must be fun.
- Avoids giving explanations, reasons.

Language: {language}
Examples of my favorites: {", ".join(favorites)}

Respond only the task itself.
"""

    response = requests.post(
        url, json={"model": model, "prompt": prompt, "stream": False}
    )
    response.raise_for_status()
    data = response.json()
    task_text = data["response"].strip()

    db = next(get_db())
    add_task_to_db(db, task_text)

    return task_text


def like_task(task_id, like):
    db = next(get_db())
    like_task_in_db(db, task_id, like)


def get_tasks(skip=0, limit=10, favorite=None):
    db = next(get_db())
    if favorite is not None:
        tasks = get_tasks_from_db(db, skip=skip, limit=limit, favorite=bool(favorite))
    else:
        tasks = get_tasks_from_db(db, skip=skip, limit=limit)

    return [
        {
            "id": task.id,
            "task_text": task.task_text,
            "created_at": task.created_at,
            "favorite": task.favorite,
        }
        for task in tasks
    ]
