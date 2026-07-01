from pathlib import Path
import json

from typer.testing import CliRunner

from routesentry_next.cli import app


FIXTURES = Path(__file__).parent / "fixtures"


def test_scan_subcommand_accepts_project_path():
    result = CliRunner().invoke(app, ["scan", str(FIXTURES / "safe_public_app")])

    assert result.exit_code == 0
    assert "Score" in result.output


def test_scan_writes_sarif_output(tmp_path):
    out = tmp_path / "routesentry.sarif"
    result = CliRunner().invoke(app, ["scan", str(FIXTURES / "middleware_only_app"), "--format", "sarif", "--out", str(out)])

    data = json.loads(out.read_text(encoding="utf-8"))
    assert result.exit_code == 0
    assert data["version"] == "2.1.0"
    assert data["runs"][0]["results"][0]["ruleId"] == "RSN-001"
