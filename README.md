# CloudDeploy CLI

> A self-hostable deployment platform. Deploy any Dockerised app with a single command — your own open-source Heroku.

```bash
clouddeploy deploy --env production
```

**Live API:** https://clouddeploy-api.onrender.com/docs

---

## Overview

CloudDeploy is a full-stack developer tool that automates the deployment lifecycle for Dockerised applications. It consists of two components:

- **CLI** — a pip-installable Python tool that builds Docker images, manages containers, streams logs, and talks to the control plane
- **Control plane** — a FastAPI REST API with JWT authentication, RBAC, and a PostgreSQL deployment history database hosted on Supabase

The CLI authenticates against the live API, records every deployment in the database, and runs containers locally via Docker. Future phases will add Oracle Cloud and AWS as remote deployment targets.

---

## Architecture

```
Developer machine
│
├── clouddeploy CLI (Python + Typer)
│   ├── Reads clouddeploy.yaml config
│   ├── Builds Docker image via Docker SDK
│   ├── Runs container locally
│   └── Records deployment → CloudDeploy API
│
└── CloudDeploy API (FastAPI, hosted on Render)
    ├── JWT authentication + RBAC (owner / developer / viewer)
    ├── Deployment history endpoints
    └── PostgreSQL on Supabase
```

---

## Tech stack

| Layer | Technology |
|-------|-----------|
| CLI | Python, Typer, Rich, Docker SDK |
| API | FastAPI, SQLAlchemy (async), Pydantic v2 |
| Auth | JWT (python-jose), bcrypt (passlib) |
| Database | PostgreSQL via Supabase |
| Hosting | Render (free tier, auto-deploy from GitHub) |
| CI/CD | GitHub (auto-deploy on push) |
| Packaging | pyproject.toml, pip editable install |

---

## Quick start

### Install the CLI

```bash
git clone https://github.com/ranacode97/clouddeploy.git
cd clouddeploy
pip install -e ".[dev]"
```

### Log in to the control plane

```bash
clouddeploy login --email you@example.com
```

### Initialise a project

```bash
cd your-app/
clouddeploy init
```

### Deploy

```bash
clouddeploy deploy
```

### Other commands

```bash
# Stream live logs
clouddeploy logs --follow

# Check status of all running deployments
clouddeploy status

# Roll back to a previous version
clouddeploy rollback --to v20260101-120000

# Show current logged-in user
clouddeploy login whoami

# Log out
clouddeploy login logout
```

---

## Config file — clouddeploy.yaml

```yaml
name: my-api
image: my-api
port: 8000
env: production
cloud: docker        # docker | oracle (Phase 4)
replicas: 1
health_check: /health
env_vars:
  DEBUG: "false"
  LOG_LEVEL: INFO
```

---

## API reference

The live API is documented at **https://clouddeploy-api.onrender.com/docs**

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/auth/register` | None | Create a new user |
| POST | `/auth/login` | None | Get JWT token |
| POST | `/auth/api-key` | Bearer | Generate API key |
| POST | `/deployments/` | Bearer | Record a deployment |
| GET | `/deployments/` | Bearer | List all deployments |
| GET | `/deployments/{id}` | Bearer | Get deployment by ID |
| PATCH | `/deployments/{id}/status` | Bearer (owner/dev) | Update status |
| DELETE | `/deployments/{id}` | Bearer (owner) | Delete deployment |

---

## Project structure

```
clouddeploy/
├── clouddeploy/                  # CLI package
│   ├── main.py                   # Typer app entry point
│   ├── config.py                 # clouddeploy.yaml loader
│   ├── api_client.py             # HTTP client for control plane
│   ├── auth_store.py             # Token storage (~/.clouddeploy/config)
│   ├── commands/
│   │   ├── login.py              # login / logout / whoami
│   │   ├── deploy.py             # build + run + record
│   │   ├── logs.py               # tail / stream logs
│   │   ├── status.py             # list running containers
│   │   ├── rollback.py           # revert to previous version
│   │   └── init.py               # interactive project setup
│   └── providers/
│       ├── __init__.py           # provider factory
│       └── docker_provider.py    # local Docker provider
│
├── server/                       # FastAPI control plane
│   ├── main.py                   # FastAPI app
│   ├── requirements.txt
│   ├── core/
│   │   ├── config.py             # pydantic-settings (.env loader)
│   │   ├── database.py           # async SQLAlchemy + Supabase
│   │   └── auth.py               # JWT + RBAC
│   ├── models/
│   │   ├── user.py               # User model (owner/developer/viewer)
│   │   └── deployment.py         # Deployment history model
│   └── routers/
│       ├── auth.py               # /auth endpoints
│       └── deployments.py        # /deployments endpoints
│
├── tests/
│   └── test_commands.py
├── render.yaml                   # Render deployment config
└── pyproject.toml
```

---

## Roadmap

| Phase | Feature | Status |
|-------|---------|--------|
| 1 | CLI scaffold — init, deploy, logs, status, rollback | ✅ Complete |
| 2 | FastAPI control plane — JWT auth, RBAC, deployment history | ✅ Complete |
| 3 | CLI ↔ API integration — login, token storage, auto-record | ✅ Complete |
| 4 | Oracle Cloud free VM provider (SSH + Docker remote) | 🔜 Planned |
| 5 | GitHub Actions integration — auto-deploy on push | 📋 Planned |
| 6 | Real-time log streaming via WebSocket | 📋 Planned |
| 7 | Kubernetes provider (k3s on free VM) | 📋 Planned |

---

## Running locally

### CLI

```bash
pip install -e ".[dev]"
clouddeploy --help
```

### API server

```bash
cp server/.env.example server/.env
# Add your DATABASE_URL and SECRET_KEY to server/.env
pip install -r server/requirements.txt
uvicorn server.main:app --reload --port 8080
# Visit http://localhost:8080/docs
```

### Tests

```bash
pytest tests/
```

---

## Design decisions

**Why Typer + Rich?** Typer gives a clean CLI API with type hints. Rich produces professional terminal output (tables, spinners, colour) with minimal code — the kind of polish that separates a portfolio project from a tutorial.

**Why FastAPI + async SQLAlchemy?** FastAPI's automatic OpenAPI docs mean the API is self-documenting out of the box. Async SQLAlchemy with asyncpg gives non-blocking database I/O, which matters when the control plane handles concurrent deploys.

**Why Supabase?** Free hosted PostgreSQL with no infrastructure to manage. The pgbouncer transaction pooler required disabling prepared statements (`statement_cache_size=0`) — a real-world configuration detail that demonstrates understanding of connection pooling.

**Why Render?** Zero-cost hosting for the control plane that deploys automatically on every `git push`. No credit card required. The trade-off (cold starts after inactivity) is acceptable for a portfolio project.

---

## Author

Shobhit Rana — [github.com/ranacode97](https://github.com/ranacode97) — [ranacode97.github.io/my-portfolio](https://ranacode97.github.io/my-portfolio/)
