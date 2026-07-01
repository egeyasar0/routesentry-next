from __future__ import annotations

from rich.console import Console
from rich.table import Table

from ..models import ScanReport


def render_console(report: ScanReport) -> None:
    console = Console()
    console.print(f"[bold]Project[/bold]: {report.project_path}")
    console.print(f"[bold]Next.js[/bold]: {report.next_version or 'not detected'}")
    console.print(f"[bold]Score[/bold]: {report.score}")
    console.print(
        f"Routes: {report.summary['total_routes']} | Protected-looking: {report.summary['protected_looking_routes']} | "
        f"Route-level auth: {report.summary['route_level_auth_detected']} | Middleware-only: {report.summary['middleware_only']} | "
        f"Matcher miss: {report.summary['matcher_miss']} | High/Medium/Low: {report.summary['high']}/{report.summary['medium']}/{report.summary['low']}"
    )

    table = Table()
    for column in ("Route", "Type", "Status", "Severity", "File"):
        table.add_column(column)
    by_route = {finding.route_path: finding.severity for finding in report.findings}
    for route in report.routes:
        table.add_row(route.path, route.route_type, route.risk_status, by_route.get(route.path, ""), str(route.source_file))
    console.print(table)

