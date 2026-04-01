import typer
from rich.console import Console
from clouddeploy.config import DeployConfig
from clouddeploy.providers import get_provider

app = typer.Typer(help="Show status of running deployments.")
console = Console()


@app.callback(invoke_without_command=True)
def status(
    ctx: typer.Context,
    app_name: str = typer.Argument(None, help="Filter by app name."),
):
    """Display all running CloudDeploy containers and their state."""
    if ctx.invoked_subcommand:
        return

    cfg      = DeployConfig.load()
    provider = get_provider(cfg.cloud)
    provider.status(name=app_name)
