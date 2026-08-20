FROM python:3.14-alpine3.23

WORKDIR /app
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN apk add --no-cache build-base
RUN pip install --no-cache-dir uv==0.11.26 && uv sync --no-dev && pip uninstall -y pip

COPY src/ ./src/

ENV BACKEND_URL=http://backend:5001

RUN addgroup -S app && adduser -S app -G app && chown -R app:app /app
USER app

ENTRYPOINT [ "uv", "run", "--no-dev", "streamlit", "run", "src/app.py", "--server.headless", "true" ]
