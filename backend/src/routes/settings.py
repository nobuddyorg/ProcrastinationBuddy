import logging
from flask import Blueprint, request, jsonify
from flask.typing import ResponseReturnValue
from services.settings import get_settings, save_settings

settings_bp = Blueprint("settings", __name__)
logger = logging.getLogger(__name__)

REQUIRED_SETTINGS = {
    "LANGUAGE": str,
    "TIMEZONE": str,
    "MODEL": str,
    "PAGE_SIZE": int,
}


def _validate_settings(payload: object) -> str | None:
    if not isinstance(payload, dict):
        return "Settings payload must be a JSON object."
    for key, expected_type in REQUIRED_SETTINGS.items():
        if key not in payload:
            return f"Missing required setting: {key}"
        value = payload[key]
        if expected_type is int:
            if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
                return f"Setting {key} must be a positive integer."
        elif not isinstance(value, expected_type) or not value:
            return f"Setting {key} must be a non-empty string."
    return None


@settings_bp.route("/settings", methods=["GET", "POST"])
def handle_settings() -> ResponseReturnValue:
    if request.method == "GET":
        try:
            record = get_settings()
        except Exception:
            logger.exception("Failed to load settings")
            return jsonify({"error": "Failed to load settings."}), 500
        return jsonify(record.settings if record else {})

    payload = request.get_json(silent=True)
    error = _validate_settings(payload)
    if error:
        return jsonify({"error": error}), 400

    try:
        save_settings(payload)
    except Exception:
        logger.exception("Failed to save settings")
        return jsonify({"error": "Failed to save settings."}), 500

    return jsonify({"message": "Settings saved"})
