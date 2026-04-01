import typer
from rich.console import Console
from clouddeploy.config import DeployConfig
from clouddeploy.providers import get_provider

app = typer.Typer(help="Roll back to a previous deployment version.")
console = Console()


@app.callback(invoke_without_command=True)
def rollback(
    ctx: typer.Context,
    app_name: str = typer.Argument(None, help="App to roll back."),
    to: str = typer.Option(..., "--to", help="Version tag to roll back to, e.g. v20240101-120000."),
    env: str = typer.Option("production", "--env", "-e"),
):
    """Revert a deployment to a specific previously-built image version."""
    if ctx.invoked_subcommand:
        return

    cfg      = DeployConfig.load()
    name     = app_name or cfg.name
    provider = get_provider(cfg.cloud)
    provider.rollback(name, env, version=to)
