import logging
import os
import re
import threading

from flask import Blueprint, jsonify, request
from flask.typing import ResponseReturnValue

from services.tasks import (
    count_tasks,
    delete_all_tasks,
    ensure_model_pulling,
    generate_task,
    get_model_status,
    like_task,
    list_tasks,
)

tasks_bp = Blueprint("tasks", __name__)
logger = logging.getLogger(__name__)
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://ollama:11434")
ollama_lock = threading.Lock()

# Ollama model names look like "name", "name:tag", or "namespace/name:tag".
MODEL_NAME_RE = re.compile(r"^[a-zA-Z0-9]([a-zA-Z0-9._:/-]{0,127})?$")


@tasks_bp.route("/tasks", methods=["POST"])
def create_task() -> ResponseReturnValue:
    data = request.get_json(silent=True) or {}
    language = data.get("language", "english")
    model = data.get("model", "mistral:instruct")

    if not isinstance(model, str) or not MODEL_NAME_RE.match(model):
        return jsonify({"error": "Invalid 'model' value."}), 400

    try:
        status = get_model_status(OLLAMA_URL, model)
        if status["status"] != "ready":
            ensure_model_pulling(OLLAMA_URL, model)
            return jsonify({"error": "Model is not ready yet.", **status}), 409

        with ollama_lock:
            task = generate_task(OLLAMA_URL, language, model)
        return jsonify({"task": task}), 201
    except Exception:
        logger.exception("Task generation failed")
        return jsonify({"error": "Task generation failed."}), 500


@tasks_bp.route("/models/status", methods=["GET"])
def model_status() -> ResponseReturnValue:
    model = request.args.get("model", "")
    if not model or not MODEL_NAME_RE.match(model):
        return jsonify({"error": "Invalid 'model' value."}), 400

    try:
        return jsonify(get_model_status(OLLAMA_URL, model)), 200
    except Exception:
        logger.exception("Failed to get model status")
        return jsonify({"error": "Failed to get model status."}), 500


@tasks_bp.route("/models/pull", methods=["POST"])
def pull_model() -> ResponseReturnValue:
    data = request.get_json(silent=True) or {}
    model = data.get("model", "")
    if not isinstance(model, str) or not model or not MODEL_NAME_RE.match(model):
        return jsonify({"error": "Invalid 'model' value."}), 400

    try:
        ensure_model_pulling(OLLAMA_URL, model)
        return jsonify(get_model_status(OLLAMA_URL, model)), 202
    except Exception:
        logger.exception("Failed to start model download")
        return jsonify({"error": "Failed to start model download."}), 500


@tasks_bp.route("/tasks", methods=["GET"])
def get_tasks() -> ResponseReturnValue:
    try:
        skip = request.args.get("skip", 0, type=int)
        limit = request.args.get("limit", 10, type=int)
        favorite = request.args.get("favorite", type=int)

        tasks = list_tasks(skip=skip, limit=limit, favorite=favorite)
        return jsonify(tasks), 200
    except Exception:
        logger.exception("Failed to fetch tasks")
        return jsonify({"error": "Failed to fetch tasks."}), 500


@tasks_bp.route("/tasks/count", methods=["GET"])
def get_task_count() -> ResponseReturnValue:
    try:
        favorite = request.args.get("favorite", type=int)
        count = count_tasks(favorite=favorite)
        return jsonify({"count": count}), 200
    except Exception:
        logger.exception("Counting tasks failed")
        return jsonify({"error": "Counting tasks failed."}), 500


@tasks_bp.route("/tasks/<int:task_id>/like", methods=["POST"])
def update_like(task_id: int) -> ResponseReturnValue:
    data = request.get_json(silent=True) or {}
    like = data.get("like")

    if like not in (0, 1):
        return jsonify({"error": "Invalid 'like' value, must be 0 or 1"}), 400

    try:
        like_task(task_id, like)
        return jsonify({"message": "Task like status updated."}), 200
    except Exception:
        logger.exception("Failed to update like status")
        return jsonify({"error": "Failed to update like status."}), 500


@tasks_bp.route("/tasks", methods=["DELETE"])
def delete_tasks() -> ResponseReturnValue:
    try:
        keep_favorites = request.args.get("keep_favorites", default=1, type=int)
        delete_all_tasks(keep_favorites=bool(keep_favorites))
        return jsonify({"message": "Task(s) deleted successfully."}), 200
    except Exception:
        logger.exception("Failed to delete tasks")
        return jsonify({"error": "Failed to delete tasks."}), 500
