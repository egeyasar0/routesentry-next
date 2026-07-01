from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer

from .analyzer import looks_like_next_project, scan_project
from .reporters.console import render_console
from .reporters.json_report import render_json
from .reporters.markdown import render_markdown
from .reporters.sarif import render_sarif


app = typer.Typer(help="Static authorization-boundary triage for Next.js routes.")


@app.callback()
def main() -> None:
    pass


@app.command()
def scan(
    nextjs_project_path: Annotated[Path, typer.Argument(exists=True, file_okay=False, dir_okay=True)],
    format: Annotated[str, typer.Option("--format", help="table, json, markdown, or sarif")] = "table",
    out: Annotated[Path | None, typer.Option("--out", help="Write json, markdown, or sarif output to a file")] = None,
    fail_on: Annotated[str | None, typer.Option("--fail-on", help="Exit 1 when severity is present: high, medium, or low")] = None,
) -> None:
    if not looks_like_next_project(nextjs_project_path):
        typer.echo("Target does not look like a Next.js project with package.json and app/ or pages/.")
        raise typer.Exit(2)

    report = scan_project(nextjs_project_path)
    if format == "json":
        text = json.dumps(render_json(report), indent=2)
    elif format == "sarif":
        text = json.dumps(render_sarif(report), indent=2)
    elif format == "markdown":
        text = render_markdown(report)
    elif format == "table":
        render_console(report)
        text = ""
    else:
        typer.echo("Unsupported format. Use table, json, markdown, or sarif.")
        raise typer.Exit(2)

    if out and text:
        out.write_text(text + "\n", encoding="utf-8")
    elif text:
        typer.echo(text)

    if fail_on and _has_severity(report, fail_on.upper()):
        raise typer.Exit(1)


def _has_severity(report, severity: str) -> bool:
    order = {"LOW": 1, "MEDIUM": 2, "HIGH": 3}
    threshold = order.get(severity)
    return bool(threshold and any(order[finding.severity] >= threshold for finding in report.findings))
