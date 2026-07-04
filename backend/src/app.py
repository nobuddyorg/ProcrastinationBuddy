import logging
from flask import Flask
from routes.tasks import tasks_bp
from routes.settings import settings_bp

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
)

app = Flask(__name__)

app.register_blueprint(tasks_bp)
app.register_blueprint(settings_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
