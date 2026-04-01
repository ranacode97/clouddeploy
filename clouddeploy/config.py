from __future__ import annotations
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from rich.console import Console

console = Console()
CONFIG_FILE = "clouddeploy.yaml"


@dataclass
class DeployConfig:
    name: str
    image: str
    port: int = 8000
    env: str = "production"
    cloud: str = "docker"          # docker | oracle | aws | azure
    replicas: int = 1
    env_vars: dict[str, str] = field(default_factory=dict)
    health_check: str = "/health"

    @classmethod
    def load(cls, path: Path | None = None) -> "DeployConfig":
        config_path = path or Path.cwd() / CONFIG_FILE
        if not config_path.exists():
            console.print(
                f"[red]✗[/] No [bold]{CONFIG_FILE}[/] found. "
                "Run [bold]clouddeploy init[/] first."
            )
            raise typer.Exit(1)
        with open(config_path) as f:
            data = yaml.safe_load(f)
        return cls(**data)

    def save(self, path: Path | None = None):
        config_path = path or Path.cwd() / CONFIG_FILE
        with open(config_path, "w") as f:
            yaml.dump(
                {k: v for k, v in self.__dict__.items() if v},
                f,
                default_flow_style=False,
            )


import typer  # noqa: E402 — imported after dataclass to keep top clean
