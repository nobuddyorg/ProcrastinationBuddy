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
    data = request.get_json(silent=True) or {}
    language = data.get("language", "english")
    model = data.get("model", "mistral:instruct")

    try:
        task = generate_task(OLLAMA_URL, language, model)
        return jsonify({"task": task}), 201
    except Exception as e:
        return jsonify({"error": f"Task generation failed: {str(e)}"}), 500


@tasks_bp.route("/tasks", methods=["GET"])
def get_tasks():
    try:
        skip = request.args.get("skip", 0, type=int)
        limit = request.args.get("limit", 10, type=int)
        favorite = request.args.get("favorite", type=int)

        tasks = list_tasks(skip=skip, limit=limit, favorite=favorite)
        return jsonify(tasks), 200
    except Exception as e:
        return jsonify({"error": f"Failed to fetch tasks: {str(e)}"}), 500


@tasks_bp.route("/tasks/count", methods=["GET"])
def get_task_count():
    try:
        favorite = request.args.get("favorite", type=int)
        count = count_tasks(favorite=favorite)
        return jsonify({"count": count}), 200
    except Exception as e:
        return jsonify({"error": f"Counting tasks failed: {str(e)}"}), 500


@tasks_bp.route("/tasks/<int:task_id>/like", methods=["POST"])
def update_like(task_id):
    data = request.get_json(silent=True) or {}
    like = data.get("like")

    if like not in (0, 1):
        return jsonify({"error": "Invalid 'like' value, must be 0 or 1"}), 400

    try:
        like_task(task_id, like)
        return jsonify({"message": "Task like status updated."}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to update like status: {str(e)}"}), 500


@tasks_bp.route("/tasks", methods=["DELETE"])
def delete_tasks():
    try:
        keep_favorites = request.args.get("keep_favorites", default=1, type=int)
        deleted = delete_all_tasks(keep_favorites=bool(keep_favorites))
        return jsonify({"message": f"{deleted} task(s) deleted successfully."}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to delete tasks: {str(e)}"}), 500
