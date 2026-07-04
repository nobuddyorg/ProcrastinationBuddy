# Contributing

Thanks for considering a contribution to Procrastination Buddy!

## Getting set up

You need **Docker** and **Docker Compose** (or **Docker Desktop**, which includes both) and a **bash** shell.

```bash
./buddy.sh start   # build images, start the stack, pull the default model
./buddy.sh test    # run the API (Bruno) and E2E (Playwright) suites
./buddy.sh stop    # stop everything
```

The app is then available at [http://localhost:8501](http://localhost:8501).

## Project layout

- `backend/` — Flask API (`src/`), unit tests (`test/`)
- `frontend/` — Streamlit UI (`src/`), unit tests (`test/`)
- `tests/api/` — Bruno API test collection
- `tests/e2e/` — Playwright end-to-end tests
- `compose.yaml` — local dev orchestration for all services

## Running checks locally

Backend and frontend each use [uv](https://docs.astral.sh/uv/) for dependency management:

```bash
cd backend  # or frontend
uv sync
uv run ruff check .
uv run pytest
```

CI (`.github/workflows/quality-gate.yaml`) runs the same lint/tests, plus the full API/E2E suite against a running stack and a container vulnerability scan (Trivy) on both Docker images. Make sure these pass before opening a pull request.

## Environment variables

See the [Environment Variables](README.md#environment-variables) section in the README, and `.env.example` for local overrides.

## Pull requests

- Keep PRs focused; unrelated changes make review harder.
- Update or add tests for behavior you change.
- Describe what changed and why in the PR description.

## Reporting bugs or security issues

- Regular bugs: open a [GitHub issue](https://github.com/nobuddyorg/ProcrastinationBuddy/issues).
- Security vulnerabilities: see [SECURITY.md](SECURITY.md) instead of opening a public issue.
