import typer
from rich.console import Console
from clouddeploy.commands import deploy, logs, status, rollback, init

app = typer.Typer(
    name="clouddeploy",
    help="[bold purple]CloudDeploy[/] — deploy Dockerised apps with a single command.",
    rich_markup_mode="rich",
    no_args_is_help=True,
)
console = Console()

app.add_typer(deploy.app,   name="deploy")
app.add_typer(logs.app,     name="logs")
app.add_typer(status.app,   name="status")
app.add_typer(rollback.app, name="rollback")
app.add_typer(init.app,     name="init")


@app.callback()
def main():
    """CloudDeploy — self-hostable deployment platform."""


if __name__ == "__main__":
    app()
