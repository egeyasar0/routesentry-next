from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class AuthDetection:
    has_route_level_auth: bool
    status: str
    patterns: list[str] = field(default_factory=list)


@dataclass
class RouteInfo:
    path: str
    route_type: str
    source_file: Path
    router: str
    http_methods: list[str] = field(default_factory=list)
    protected_looking: bool = False
    has_route_level_auth: bool = False
    covered_by_middleware: bool = False
    risk_status: str = "manual_review"


@dataclass
class MiddlewareInfo:
    exists: bool
    source_file: Path | None = None
    matchers: list[str] = field(default_factory=list)
    broad: bool = False

    def covers(self, route_path: str) -> bool:
        if not self.exists:
            return False
        if self.broad:
            return True
        return any(matcher_covers(matcher, route_path) for matcher in self.matchers)


@dataclass
class Finding:
    rule_id: str
    severity: str
    confidence: str
    route_path: str
    source_file: Path
    message: str
    recommendation: str


@dataclass
class ScanReport:
    schema_version: str
    project_path: Path
    scan_timestamp: str
    next_version: str | None
    score: int
    summary: dict[str, int]
    routes: list[RouteInfo]
    findings: list[Finding]


def matcher_covers(matcher: str, route_path: str) -> bool:
    if matcher.startswith("/((?!"):
        excluded = matcher.split("/((?!", 1)[1].split(")", 1)[0].split("|")
        first = route_path.strip("/").split("/", 1)[0]
        return first not in excluded
    if matcher.endswith("/:path*"):
        prefix = matcher.removesuffix("/:path*")
        return route_path == prefix or route_path.startswith(prefix + "/")
    return route_path == matcher


def to_plain(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    if hasattr(value, "__dataclass_fields__"):
        return {key: to_plain(item) for key, item in asdict(value).items()}
    if isinstance(value, list):
        return [to_plain(item) for item in value]
    if isinstance(value, dict):
        return {key: to_plain(item) for key, item in value.items()}
    return value

