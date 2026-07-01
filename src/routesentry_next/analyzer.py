from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

from .auth_detector import detect_route_auth
from .middleware_parser import parse_middleware
from .models import Finding, ScanReport
from .route_mapper import map_routes
from .scoring import score


MUTATION_METHODS = {"POST", "PUT", "PATCH", "DELETE"}


def scan_project(project_path: Path) -> ScanReport:
    project_path = Path(project_path)
    next_version = detect_next_version(project_path)
    middleware = parse_middleware(project_path)
    routes = map_routes(project_path)
    findings: list[Finding] = []

    for route in routes:
        auth = detect_route_auth(route.source_file)
        route.has_route_level_auth = auth.has_route_level_auth
        route.covered_by_middleware = middleware.covers(route.path)

        if route.has_route_level_auth:
            route.risk_status = "route_level_auth_detected"
            continue
        if route.route_type in {"api_route", "route_handler"} and MUTATION_METHODS.intersection(route.http_methods):
            route.risk_status = "mutation_without_auth"
            findings.append(_finding("RSN-003", "HIGH", "high", route))
            continue
        if route.protected_looking and middleware.exists and route.covered_by_middleware:
            route.risk_status = "middleware_only"
            findings.append(_finding("RSN-001", "HIGH" if route.route_type != "page" else "MEDIUM", "high", route))
            continue
        if route.protected_looking and middleware.exists and not route.covered_by_middleware:
            route.risk_status = "matcher_miss"
            findings.append(_finding("RSN-002", "HIGH", "medium", route))
            continue
        route.risk_status = "public_or_not_protected_looking" if not route.protected_looking else "manual_review"

    summary = _summary(routes, findings)
    return ScanReport(
        schema_version="1.0",
        project_path=project_path,
        scan_timestamp=datetime.now(timezone.utc).isoformat(),
        next_version=next_version,
        score=score(findings),
        summary=summary,
        routes=routes,
        findings=findings,
    )


def looks_like_next_project(project_path: Path) -> bool:
    project_path = Path(project_path)
    route_dirs = ("app", "pages", "src/app", "src/pages")
    return bool(detect_next_version(project_path) and any((project_path / route_dir).exists() for route_dir in route_dirs))


def detect_next_version(project_path: Path) -> str | None:
    package_file = Path(project_path) / "package.json"
    if not package_file.exists():
        return None
    package = json.loads(package_file.read_text(encoding="utf-8"))
    for section in ("dependencies", "devDependencies"):
        version = package.get(section, {}).get("next")
        if version:
            return version
    return None


def _finding(rule_id: str, severity: str, confidence: str, route) -> Finding:
    messages = {
        "RSN-001": "Route appears to rely on middleware/proxy coverage without a detectable route-level authorization check.",
        "RSN-002": "Protected-looking route is not covered by middleware/proxy matcher and no route-level authorization pattern was detected.",
        "RSN-003": "Mutation endpoint has no detectable route-level authorization pattern.",
    }
    recommendations = {
        "RSN-001": "Add route-level session/role validation and return 401/403 for unauthorized access. Middleware should be a first gate, not the only authorization boundary.",
        "RSN-002": "Update matcher coverage or add route-level authorization checks.",
        "RSN-003": "Require session/user validation before performing mutations and return 401/403 when unauthorized.",
    }
    return Finding(rule_id, severity, confidence, route.path, route.source_file, messages[rule_id], recommendations[rule_id])


def _summary(routes, findings: list[Finding]) -> dict[str, int]:
    return {
        "total_routes": len(routes),
        "protected_looking_routes": sum(route.protected_looking for route in routes),
        "route_level_auth_detected": sum(route.has_route_level_auth for route in routes),
        "middleware_only": sum(route.risk_status == "middleware_only" for route in routes),
        "matcher_miss": sum(route.risk_status == "matcher_miss" for route in routes),
        "high": sum(finding.severity == "HIGH" for finding in findings),
        "medium": sum(finding.severity == "MEDIUM" for finding in findings),
        "low": sum(finding.severity == "LOW" for finding in findings),
    }
