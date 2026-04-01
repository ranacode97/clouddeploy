from unittest.mock import MagicMock, patch
from typer.testing import CliRunner
from clouddeploy.main import app

runner = CliRunner()


def test_deploy_dry_run(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    config = tmp_path / "clouddeploy.yaml"
    config.write_text(
        "name: test-app\nimage: test-app\nport: 8000\nenv: production\ncloud: docker\nreplicas: 1\n"
    )
    result = runner.invoke(app, ["deploy", "--dry-run"])
    assert result.exit_code == 0
    assert "Dry run" in result.output


def test_status_no_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["status"])
    assert "clouddeploy.yaml" in result.output


def test_init_creates_config(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    result = runner.invoke(app, ["init"], input="my-app\nmy-app\n8080\nstaging\ndocker\n")
    assert result.exit_code == 0
    assert (tmp_path / "clouddeploy.yaml").exists()
