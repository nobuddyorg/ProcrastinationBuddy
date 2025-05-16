from flask import Blueprint, request, jsonify
from src.services.settings import get_settings, save_settings

settings_bp = Blueprint("settings", __name__)


@settings_bp.route("/settings", methods=["GET", "POST"])
def handle_settings():
    if request.method == "GET":
        record = get_settings()
        return jsonify(record.settings if record else {})
    else:
        settings = request.json
        save_settings(settings)
        return jsonify({"message": "Settings saved"})
