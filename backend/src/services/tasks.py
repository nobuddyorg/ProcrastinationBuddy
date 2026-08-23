import json
import threading

import requests
from sqlalchemy.orm import Session

from db.db import (
    add_task_to_db,
    count_tasks_in_db,
    delete_tasks_in_db,
    get_tasks_from_db,
    like_task_in_db,
    with_db_session,
)

_pull_state: dict[str, dict] = {}
_pull_state_lock = threading.Lock()


def _set_pull_state(model: str, **fields) -> None:
    with _pull_state_lock:
        _pull_state.setdefault(model, {}).update(fields)


def _get_pull_state(model: str) -> dict:
    with _pull_state_lock:
        return dict(_pull_state.get(model, {}))


def model_available(url: str, model: str) -> bool:
    """Check with Ollama whether `model` has already been pulled."""
    tags_response = requests.get(f"{url}/api/tags")
    tags_response.raise_for_status()
    models = [m["name"] for m in tags_response.json().get("models", [])]
    return model in models


def get_model_status(url: str, model: str) -> dict:
    """Return the current readiness of `model`: ready, downloading, error or not_downloaded."""
    state = _get_pull_state(model)
    status = state.get("status")

    if status == "downloading":
        return {
            "status": "downloading",
            "detail": state.get("detail", ""),
            "completed": state.get("completed", 0),
            "total": state.get("total", 0),
        }
    if status == "error":
        return {"status": "error", "error": state.get("error", "")}
    if status == "ready":
        return {"status": "ready"}

    if model_available(url, model):
        _set_pull_state(model, status="ready")
        return {"status": "ready"}
    return {"status": "not_downloaded"}


def ensure_model_pulling(url: str, model: str) -> None:
    """Kick off a background download of `model` if it isn't ready or already downloading."""
    if _get_pull_state(model).get("status") == "downloading":
        return
    if model_available(url, model):
        _set_pull_state(model, status="ready")
        return

    thread = threading.Thread(target=_run_pull, args=(url, model), daemon=True)
    thread.start()


def _run_pull(url: str, model: str) -> None:
    try:
        _set_pull_state(model, status="downloading", detail="starting", completed=0, total=0)
        with requests.post(
            f"{url}/api/pull", json={"name": model, "stream": True}, stream=True
        ) as pull_response:
            pull_response.raise_for_status()
            for line in pull_response.iter_lines():
                if not line:
                    continue
                data = json.loads(line)
                fields = {"status": "downloading", "detail": data.get("status", "")}
                # completed/total describe the current layer and must come from
                # the same message - each layer has its own size, so pairing a
                # stale value from a differently-sized layer with a fresh one
                # can push the ratio outside [0, 1].
                if "completed" in data and "total" in data:
                    fields["completed"] = data["completed"]
                    fields["total"] = data["total"]
                _set_pull_state(model, **fields)
        _set_pull_state(model, status="ready")
    except Exception as e:  # noqa: BLE001 - top-level boundary for a daemon thread; must not let any error kill it silently
        _set_pull_state(model, status="error", error=str(e))


@with_db_session
def generate_task(db: Session, url: str, language: str, model: str) -> str:
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


def generate_prompt(language: str) -> str:
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
def like_task(db: Session, task_id: int, like: int) -> None:
    like_task_in_db(db, task_id, like)


@with_db_session
def list_tasks(
    db: Session, skip: int = 0, limit: int = 10, favorite: bool | None = None
) -> list[dict]:
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
def count_tasks(db: Session, favorite: bool | None = None) -> int:
    return count_tasks_in_db(db, favorite=favorite)


@with_db_session
def delete_all_tasks(db: Session, keep_favorites: bool = True) -> None:
    delete_tasks_in_db(db, keep_favorites=keep_favorites)
