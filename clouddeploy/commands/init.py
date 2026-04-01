import typer
from pathlib import Path
from rich.console import Console
from rich.prompt import Prompt, IntPrompt
from clouddeploy.config import DeployConfig, CONFIG_FILE

app = typer.Typer(help="Initialise a new CloudDeploy project.")
console = Console()


@app.callback(invoke_without_command=True)
def init(ctx: typer.Context):
    """Interactively create a clouddeploy.yaml in the current directory."""
    if ctx.invoked_subcommand:
        return

    config_path = Path.cwd() / CONFIG_FILE
    if config_path.exists():
        overwrite = Prompt.ask(
            f"[yellow]{CONFIG_FILE} already exists. Overwrite?[/]",
            choices=["y", "n"],
            default="n",
        )
        if overwrite == "n":
            raise typer.Exit()

    console.print("\n[bold purple]CloudDeploy[/] — new project setup\n")

    name    = Prompt.ask("  App name",     default=Path.cwd().name)
    image   = Prompt.ask("  Docker image", default=name)
    port    = IntPrompt.ask("  Port",       default=8000)
    env     = Prompt.ask("  Environment",  default="production")
    cloud   = Prompt.ask("  Cloud target", choices=["docker", "oracle", "aws", "azure"], default="docker")

    cfg = DeployConfig(name=name, image=image, port=port, env=env, cloud=cloud)
    cfg.save()

    console.print(f"\n[green]✓[/] Created [bold]{CONFIG_FILE}[/]")
    console.print(f"  Run [bold]clouddeploy deploy[/] when you're ready.\n")
