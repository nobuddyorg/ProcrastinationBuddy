FROM python:3.13-alpine3.21

WORKDIR /app
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN pip install --no-cache-dir uv==0.9.3 && uv sync

COPY src/ ./src/

ENV BACKEND_URL=http://backend:5001

ENTRYPOINT [ "uv", "run", "streamlit", "run", "src/app.py", " --server.headless", "true" ]
