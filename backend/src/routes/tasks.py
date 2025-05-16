from flask import Blueprint, request, jsonify
from src.services.tasks import (
    generate_task,
    list_tasks,
    count_tasks,
    like_task,
    delete_all_tasks,
)

tasks_bp = Blueprint("tasks", __name__)

OLLAMA_URL = "http://ollama:11434"


@tasks_bp.route("/tasks", methods=["POST"])
def create_task():
    data = request.json or {}
    language = data.get("language", "english")
    model = data.get("model", "mistral:instruct")

    try:
        task = generate_task(OLLAMA_URL, language, model)
        return jsonify({"task": task}), 201
    except Exception as e:
        return jsonify({"error": f"Task generation failed: {str(e)}"}), 500


@tasks_bp.route("/tasks", methods=["GET"])
def get_tasks():
    skip = request.args.get("skip", 0, type=int)
    limit = request.args.get("limit", 10, type=int)
    favorite = request.args.get("favorite", type=int)
    tasks = list_tasks(skip=skip, limit=limit, favorite=favorite)
    return jsonify(tasks)


@tasks_bp.route("/tasks/count", methods=["GET"])
def get_task_count():
    favorite = request.args.get("favorite", type=int)
    try:
        count = count_tasks(favorite=favorite)
        return jsonify({"count": count})
    except Exception:
        return jsonify({"error": "Counting tasks failed."}), 500


@tasks_bp.route("/tasks/<int:task_id>/like", methods=["POST"])
def update_like(task_id):
    data = request.json or {}
    like = data.get("like")
    if like not in (0, 1):
        return jsonify({"error": "Invalid 'like' value, must be 0 or 1"}), 400

    like_task(task_id, like)
    return jsonify({"message": "Task like status updated."})


@tasks_bp.route("/tasks", methods=["DELETE"])
def delete_tasks():
    keep_favorites = request.args.get("keep_favorites", default=1, type=int)
    delete_all_tasks(keep_favorites=bool(keep_favorites))
    return jsonify({"message": "Tasks deleted successfully."})
