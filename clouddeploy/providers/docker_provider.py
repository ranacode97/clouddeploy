from __future__ import annotations
import docker
import docker.errors
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from datetime import datetime

console = Console()


class DockerProvider:
    """Manages local Docker deployments — great for dev and free-tier VPS targets."""

    def __init__(self):
        try:
            self.client = docker.from_env()
            self.client.ping()
        except docker.errors.DockerException:
            console.print("[red]✗[/] Docker daemon is not running. Please start Docker.")
            raise SystemExit(1)

    # ------------------------------------------------------------------
    # Build
    # ------------------------------------------------------------------
    def build(self, name: str, tag: str, context: str = ".") -> str:
        """Build a Docker image from the current directory."""
        image_tag = f"{name}:{tag}"
        console.print(f"[dim]Building image[/] [bold]{image_tag}[/]…")

        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task("Building…", total=None)
            image, build_logs = self.client.images.build(
                path=context,
                tag=image_tag,
                rm=True,
            )
            for chunk in build_logs:
                if "stream" in chunk:
                    line = chunk["stream"].strip()
                    if line:
                        progress.update(task, description=f"[dim]{line[:72]}[/]")

        console.print(f"[green]✓[/] Built [bold]{image_tag}[/] ({image.short_id})")
        return image_tag

    # ------------------------------------------------------------------
    # Deploy
    # ------------------------------------------------------------------
    def deploy(self, config) -> str:
        """Run (or replace) a container for the given config."""
        tag = datetime.now().strftime("v%Y%m%d-%H%M%S")
        image_tag = self.build(config.name, tag)

        container_name = f"cd-{config.name}-{config.env}"
        self._stop_existing(container_name)

        console.print(f"[dim]Starting container[/] [bold]{container_name}[/]…")
        container = self.client.containers.run(
            image_tag,
            name=container_name,
            detach=True,
            restart_policy={"Name": "unless-stopped"},
            ports={f"{config.port}/tcp": config.port},
            environment=config.env_vars,
            labels={
                "clouddeploy.app": config.name,
                "clouddeploy.env": config.env,
                "clouddeploy.version": tag,
            },
        )
        console.print(
            f"[green]✓[/] Deployed [bold]{config.name}[/] "
            f"→ http://localhost:{config.port}  [dim]({container.short_id})[/]"
        )
        return tag

    # ------------------------------------------------------------------
    # Logs
    # ------------------------------------------------------------------
    def logs(self, name: str, env: str, follow: bool = False, tail: int = 50):
        container = self._get_container(name, env)
        if not container:
            return
        if follow:
            console.print(f"[dim]Streaming logs for[/] [bold]{name}[/] (Ctrl+C to stop)…\n")
            for line in container.logs(stream=True, follow=True):
                console.print(line.decode().rstrip())
        else:
            output = container.logs(tail=tail).decode()
            console.print(output)

    # ------------------------------------------------------------------
    # Status
    # ------------------------------------------------------------------
    def status(self, name: str | None = None):
        filters = {"label": "clouddeploy.app"}
        if name:
            filters["label"] = f"clouddeploy.app={name}"

        containers = self.client.containers.list(all=True, filters=filters)
        if not containers:
            console.print("[yellow]No deployments found.[/]")
            return

        table = Table(show_header=True, header_style="bold", box=None, pad_edge=False)
        table.add_column("App",     style="bold")
        table.add_column("Env",     style="dim")
        table.add_column("Version", style="dim")
        table.add_column("Status")
        table.add_column("Port")

        for c in containers:
            labels = c.labels
            state  = c.status
            colour = "green" if state == "running" else "red"
            ports  = ", ".join(
                str(p["HostPort"])
                for bindings in (c.ports or {}).values()
                for p in (bindings or [])
            ) or "—"
            table.add_row(
                labels.get("clouddeploy.app", "—"),
                labels.get("clouddeploy.env", "—"),
                labels.get("clouddeploy.version", "—"),
                f"[{colour}]{state}[/]",
                ports,
            )
        console.print(table)

    # ------------------------------------------------------------------
    # Rollback
    # ------------------------------------------------------------------
    def rollback(self, name: str, env: str, version: str):
        image_tag = f"{name}:{version}"
        try:
            self.client.images.get(image_tag)
        except docker.errors.ImageNotFound:
            console.print(f"[red]✗[/] Image [bold]{image_tag}[/] not found locally.")
            return

        container_name = f"cd-{name}-{env}"
        self._stop_existing(container_name)

        console.print(f"[dim]Rolling back to[/] [bold]{version}[/]…")
        self.client.containers.run(
            image_tag,
            name=container_name,
            detach=True,
            restart_policy={"Name": "unless-stopped"},
            labels={
                "clouddeploy.app": name,
                "clouddeploy.env": env,
                "clouddeploy.version": version,
            },
        )
        console.print(f"[green]✓[/] Rolled back [bold]{name}[/] to [bold]{version}[/]")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _get_container(self, name: str, env: str):
        containers = self.client.containers.list(
            filters={"label": [f"clouddeploy.app={name}", f"clouddeploy.env={env}"]}
        )
        if not containers:
            console.print(f"[red]✗[/] No running container found for [bold]{name}[/] ({env})")
            return None
        return containers[0]

    def _stop_existing(self, container_name: str):
        try:
            old = self.client.containers.get(container_name)
            console.print(f"[dim]Stopping existing container[/] {container_name}…")
            old.stop(timeout=5)
            old.remove()
        except docker.errors.NotFound:
            pass
