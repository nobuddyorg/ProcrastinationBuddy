FROM python:3.13-alpine3.21

WORKDIR /app
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN pip install uv && uv sync

COPY src/ ./src/

ENTRYPOINT [ "uv", "run", "src/app.py" ]
