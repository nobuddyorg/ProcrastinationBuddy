FROM python:3.13-alpine3.21

WORKDIR /app
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN pip install uv && uv sync

COPY app.py app.py
COPY config/config.py config/config.py
COPY procrastination/procrastination.py procrastination/procrastination.py

ENTRYPOINT [ "uv", "run", "app.py", "--url=http://ollama:11434/api/generate" ]
