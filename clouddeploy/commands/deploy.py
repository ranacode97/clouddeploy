import typer
from typing import Optional
from rich.console import Console
from clouddeploy.config import DeployConfig
from clouddeploy.providers import get_provider

app = typer.Typer(help="Deploy your app to the configured cloud target.")
console = Console()


@app.callback(invoke_without_command=True)
def deploy(
    ctx: typer.Context,
    env: Optional[str] = typer.Option(None, "--env", "-e", help="Override environment name."),
    cloud: Optional[str] = typer.Option(None, "--cloud", "-c", help="Override cloud target."),
    dry_run: bool = typer.Option(False, "--dry-run", help="Print what would happen without deploying."),
):
    """Build and deploy your Dockerised app."""
    if ctx.invoked_subcommand:
        return

    cfg = DeployConfig.load()
    if env:
        cfg.env = env
    if cloud:
        cfg.cloud = cloud

    console.rule(f"[bold]Deploying [purple]{cfg.name}[/] → {cfg.cloud} ({cfg.env})[/]")

    if dry_run:
        console.print(f"\n[yellow]Dry run:[/] would deploy [bold]{cfg.name}[/] "
                      f"to [bold]{cfg.cloud}[/] in env [bold]{cfg.env}[/]")
        console.print(f"  image: {cfg.image}   port: {cfg.port}   replicas: {cfg.replicas}\n")
        return

    provider = get_provider(cfg.cloud)
    version  = provider.deploy(cfg)
    console.rule(f"[green]Done — {cfg.name} {version}[/]")
