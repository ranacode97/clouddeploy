# CloudDeploy CLI

> A self-hostable deployment platform. Deploy any Dockerised app with a single command.

```bash
clouddeploy deploy --env production
```

---

## Features (Phase 1)

- `clouddeploy init` — interactive project setup, creates `clouddeploy.yaml`
- `clouddeploy deploy` — builds Docker image and runs it locally or on a remote target
- `clouddeploy logs` — tail or stream live container logs
- `clouddeploy status` — table view of all running deployments
- `clouddeploy rollback --to v20240101-120000` — instant rollback to any previous build

## Architecture

```
clouddeploy/
├── main.py              # CLI entry point (Typer)
├── config.py            # clouddeploy.yaml loader
├── commands/
│   ├── init.py          # clouddeploy init
│   ├── deploy.py        # clouddeploy deploy
│   ├── logs.py          # clouddeploy logs
│   ├── status.py        # clouddeploy status
│   └── rollback.py      # clouddeploy rollback
└── providers/
    ├── __init__.py      # provider factory
    └── docker_provider.py  # Phase 1: local Docker
    # oracle_provider.py    # Phase 3: Oracle Cloud free tier
    # aws_provider.py       # Phase 3: AWS ECS
```

## Quick start

```bash
# Install
pip install -e ".[dev]"

# Initialise a project
cd your-app/
clouddeploy init

# Deploy
clouddeploy deploy

# Stream logs
clouddeploy logs --follow

# Check status
clouddeploy status

# Roll back
clouddeploy rollback --to v20240101-120000
```

## Config file — clouddeploy.yaml

```yaml
name: my-api
image: my-api
port: 8000
env: production
cloud: docker        # docker | oracle | aws | azure
replicas: 1
health_check: /health
env_vars:
  DEBUG: "false"
  LOG_LEVEL: INFO
```

## Roadmap

| Phase | Feature | Status |
|-------|---------|--------|
| 1 | CLI scaffold + Docker provider | ✅ Done |
| 2 | FastAPI control plane + JWT auth | 🔜 Next |
| 3 | Oracle Cloud / AWS / Azure providers | 📋 Planned |
| 4 | Kubernetes + GitHub Actions + metrics | 📋 Planned |

## Tech stack

Python · Typer · Rich · Docker SDK · PyYAML · pytest

---

Built as a portfolio project to demonstrate Python CLI engineering, Docker integration, and cloud deployment concepts.
