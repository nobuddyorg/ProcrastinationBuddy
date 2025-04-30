FROM python:3.13-alpine3.21

WORKDIR /app
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN pip install uv && uv sync

COPY img/eisenhower.png img/eisenhower.png
COPY img/pomodoro.png img/pomodoro.png
COPY app.py app.py
COPY constants.py constants.py
COPY utils.py utils.py

ENV BACKEND_URL=http://backend:5000

ENTRYPOINT [ "uv", "run", "streamlit", "run", "app.py", " --server.headless", "true" ]
