from flask import Flask, jsonify, request
from procrastination.procrastination import (
    procrastinate,
    get_tasks,
    like_task,
    count_tasks,
    delete_tasks,
    get_app_settings,
    save_app_settings,
)
from config.config import get_config
import requests

app = Flask(__name__)

app.config["EXCUSE_API_URL"] = get_config()


@app.route("/procrastinate", methods=["GET"])
def procrastinate_endpoint():
    url = request.args.get("url", app.config["EXCUSE_API_URL"])
    language = request.args.get("language", "english")
    model = request.args.get("model", "mistral:instruct")
    try:
        task = procrastinate(url, language=language, model=model)
        return jsonify({"task": task})
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Task generation failed."}), 500


@app.route("/tasks", methods=["GET"])
def get_tasks_endpoint():
    skip = request.args.get("skip", 0, type=int)
    limit = request.args.get("limit", 10, type=int)
    favorite = request.args.get("favorite", type=int)

    tasks = get_tasks(skip=skip, limit=limit, favorite=favorite)

    return jsonify(tasks)


@app.route("/tasks/like", methods=["POST"])
def like_task_endpoint():
    task_id = request.args.get("task_id", type=int)
    like = request.args.get("like", type=int)

    if task_id is None or like not in (0, 1):
        return jsonify({"error": "Missing or invalid task_id or like parameter"}), 400

    like_task(task_id, like)

    return jsonify({"message": "success"})


@app.route("/tasks/count", methods=["GET"])
def count_tasks_endpoint():
    favorite = request.args.get("favorite", type=int)
    try:
        total = count_tasks(favorite=favorite)
        return jsonify({"count": total})
    except Exception as e:
        return jsonify({"error": "Counting tasks failed."}), 500


@app.route("/tasks", methods=["DELETE"])
def delete_tasks_endpoint():
    keep_favorites = request.args.get("keep_favorites", default=1, type=int)

    delete_tasks(keep_favorites=bool(keep_favorites))
    return jsonify({"message": "Tasks deleted successfully."}), 200


@app.route("/settings", methods=["GET", "POST"])
def settings_endpoint():
    if request.method == "GET":
        record = get_app_settings()
        return jsonify(record.settings if record else {})
    elif request.method == "POST":
        settings = request.json
        save_app_settings(settings)
        return jsonify({"message": "Settings saved"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
