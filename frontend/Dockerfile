FROM python:3.14-alpine3.23

WORKDIR /app
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN apk add --no-cache build-base
RUN pip install --no-cache-dir uv==0.9.16 && uv sync

COPY src/ ./src/

ENV BACKEND_URL=http://backend:5001

ENTRYPOINT [ "uv", "run", "streamlit", "run", "src/app.py", " --server.headless", "true" ]
