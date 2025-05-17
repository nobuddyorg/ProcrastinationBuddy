FROM python:3.13-alpine3.21

WORKDIR /app
COPY pyproject.toml pyproject.toml
COPY uv.lock uv.lock

RUN pip install uv && uv sync

COPY src/app.py src/app.py
COPY src/ui/img/eisenhower.png src/ui/img/eisenhower.png
COPY src/ui/img/pomodoro.png src/ui/img/pomodoro.png
COPY src/ui/ui.py src/ui/ui.py
COPY src/utils/constants.py src/utils/constants.py
COPY src/utils/utils.py src/utils/utils.py

ENV BACKEND_URL=http://backend:5000

ENTRYPOINT [ "uv", "run", "streamlit", "run", "src/app.py", " --server.headless", "true" ]
