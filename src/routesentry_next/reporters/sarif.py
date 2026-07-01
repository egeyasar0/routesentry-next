from __future__ import annotations

from pathlib import Path

from ..models import Finding, ScanReport


RULES = {
    "RSN-001": {
        "name": "Middleware-only protected route",
        "shortDescription": {"text": "Protected-looking route relies on middleware without detectable route-level auth."},
        "help": {"text": "Add route-level session/role validation. Middleware should be a first gate, not the only authorization boundary."},
    },
    "RSN-002": {
        "name": "Protected-looking route missed by middleware",
        "shortDescription": {"text": "Protected-looking route is not covered by middleware and lacks detectable route-level auth."},
        "help": {"text": "Update matcher coverage or add route-level authorization checks."},
    },
    "RSN-003": {
        "name": "Mutation API without detectable auth",
        "shortDescription": {"text": "Mutation endpoint has no detectable route-level authorization pattern."},
        "help": {"text": "Require session/user validation before mutations and return 401/403 when unauthorized."},
    },
}

LEVELS = {"HIGH": "error", "MEDIUM": "warning", "LOW": "note", "INFO": "note"}


def render_sarif(report: ScanReport) -> dict:
    routes_by_path = {route.path: route for route in report.routes}
    return {
        "$schema": "https://json.schemastore.org/sarif-2.1.0.json",
        "version": "2.1.0",
        "runs": [
            {
                "tool": {
                    "driver": {
                        "name": "RouteSentry Next",
                        "informationUri": "https://github.com/routesentry-next/routesentry-next",
                        "rules": [_rule(rule_id, metadata) for rule_id, metadata in RULES.items()],
                    }
                },
                "results": [_result(finding, routes_by_path.get(finding.route_path)) for finding in report.findings],
            }
        ],
    }


def _rule(rule_id: str, metadata: dict) -> dict:
    return {"id": rule_id, **metadata}


def _result(finding: Finding, route) -> dict:
    return {
        "ruleId": finding.rule_id,
        "level": LEVELS.get(finding.severity, "note"),
        "message": {"text": finding.message},
        "locations": [
            {
                "physicalLocation": {
                    "artifactLocation": {"uri": _uri(finding.source_file)},
                    "region": {"startLine": 1},
                }
            }
        ],
        "properties": {
            "confidence": finding.confidence,
            "route": finding.route_path,
            "route_type": route.route_type if route else "",
            "status": route.risk_status if route else "",
            "recommendation": finding.recommendation,
        },
    }


def _uri(path: Path) -> str:
    return path.as_posix()
