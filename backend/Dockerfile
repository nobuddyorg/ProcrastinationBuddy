FROM python:3.13-alpine3.21

WORKDIR /app
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN pip install uv && uv sync

COPY app.py app.py
COPY src/db/db.py src/db/db.py
COPY src/services/tasks.py src/services/tasks.py
COPY src/services/settings.py src/services/settings.py
COPY src/routes/tasks.py src/routes/tasks.py
COPY src/routes/settings.py src/routes/settings.py

ENTRYPOINT [ "uv", "run", "app.py" ]
