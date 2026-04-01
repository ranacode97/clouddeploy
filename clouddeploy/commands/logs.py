import typer
from rich.console import Console
from clouddeploy.config import DeployConfig
from clouddeploy.providers import get_provider

app = typer.Typer(help="Stream or tail logs from a deployed app.")
console = Console()


@app.callback(invoke_without_command=True)
def logs(
    ctx: typer.Context,
    app_name: str = typer.Argument(None, help="App name (defaults to config name)."),
    follow: bool = typer.Option(False, "--follow", "-f", help="Stream logs live."),
    tail: int = typer.Option(50, "--tail", "-n", help="Number of lines to show."),
    env: str = typer.Option("production", "--env", "-e"),
):
    """Fetch or stream logs from a running deployment."""
    if ctx.invoked_subcommand:
        return

    cfg      = DeployConfig.load()
    name     = app_name or cfg.name
    provider = get_provider(cfg.cloud)
    provider.logs(name, env, follow=follow, tail=tail)
