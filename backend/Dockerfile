FROM python:3.14-alpine3.21

WORKDIR /app
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN pip install --no-cache-dir uv==0.7.5 && uv sync

COPY src/ ./src/

ENTRYPOINT [ "uv", "run", "src/app.py" ]
