from __future__ import annotations

from ..models import ScanReport


def render_markdown(report: ScanReport) -> str:
    lines = [
        "# RouteSentry Next Report",
        "",
        "## Summary",
        f"- Project: `{report.project_path}`",
        f"- Next.js version: `{report.next_version or 'not detected'}`",
        f"- Score: {report.score}",
        f"- Total routes: {report.summary['total_routes']}",
        f"- Protected-looking routes: {report.summary['protected_looking_routes']}",
        "",
        "## Findings by Severity",
    ]
    if report.findings:
        for finding in report.findings:
            lines.append(f"- **{finding.severity}** `{finding.rule_id}` `{finding.route_path}`: {finding.message}")
    else:
        lines.append("- No MVP findings.")

    lines += [
        "",
        "## Route Authorization Map",
        "| Route | Type | Status | File |",
        "| --- | --- | --- | --- |",
    ]
    for route in report.routes:
        lines.append(f"| `{route.path}` | {route.route_type} | {route.risk_status} | `{route.source_file}` |")

    lines += ["", "## Detailed Findings"]
    if report.findings:
        for finding in report.findings:
            lines += [
                f"### {finding.rule_id}: {finding.route_path}",
                f"- Severity: {finding.severity}",
                f"- Confidence: {finding.confidence}",
                f"- Message: {finding.message}",
                f"- Recommendation: {finding.recommendation}",
            ]
    else:
        lines.append("No detailed findings.")

    lines += [
        "",
        "## Limitations",
        "- RouteSentry Next does not prove a route is secure or insecure.",
        "- Matcher parsing supports common string and array forms, not full Next.js matcher semantics.",
        "- Auth detection uses conservative static patterns and may miss custom authorization code.",
        "",
        "## Recommendations",
        "- Review each finding manually.",
        "- Add route-level session or role checks on sensitive routes.",
        "- Use middleware as a first gate, not the only authorization boundary.",
        "",
    ]
    return "\n".join(lines)

