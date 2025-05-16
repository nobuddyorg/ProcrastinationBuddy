from flask import Flask
from src.routes.tasks import tasks_bp
from src.routes.settings import settings_bp

app = Flask(__name__)

app.register_blueprint(tasks_bp)
app.register_blueprint(settings_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
