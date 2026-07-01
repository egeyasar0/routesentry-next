from __future__ import annotations

import re
from pathlib import Path

from .models import RouteInfo


HTTP_METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"]
PROTECTED_PREFIXES = (
    "/admin",
    "/dashboard",
    "/settings",
    "/profile",
    "/account",
    "/billing",
    "/api/admin",
    "/api/user",
    "/api/users",
    "/api/me",
    "/api/account",
    "/api/billing",
    "/api/settings",
    "/api/private",
    "/api/internal",
)


def map_routes(project_path: Path) -> list[RouteInfo]:
    project_path = Path(project_path)
    routes: list[RouteInfo] = []

    for app_dir in _existing_dirs(project_path, ("app", "src/app")):
        for source in sorted(app_dir.rglob("*")):
            if source.name not in {"page.ts", "page.tsx", "route.ts", "route.tsx"}:
                continue
            parts = source.relative_to(app_dir).parent.parts
            if _has_private_part(parts):
                continue
            route_type = "page" if source.name.startswith("page.") else "route_handler"
            route_path = _route_from_parts(parts)
            routes.append(
                RouteInfo(
                    path=route_path,
                    route_type=route_type,
                    source_file=source,
                    router="app",
                    http_methods=_detect_methods(source) if route_type == "route_handler" else [],
                    protected_looking=is_protected_path(route_path),
                )
            )

    for pages_dir in _existing_dirs(project_path, ("pages", "src/pages")):
        for source in sorted(pages_dir.rglob("*.ts*")):
            if source.name.startswith("_") or source.name.endswith(".d.ts"):
                continue
            relative = source.relative_to(pages_dir)
            if _has_private_part(relative.parts):
                continue
            is_api = relative.parts[0] == "api"
            route_path = _route_from_parts(relative.with_suffix("").parts)
            routes.append(
                RouteInfo(
                    path=route_path,
                    route_type="api_route" if is_api else "page",
                    source_file=source,
                    router="pages",
                    http_methods=_detect_methods(source) if is_api else [],
                    protected_looking=is_protected_path(route_path),
                )
            )

    return routes


def _existing_dirs(project_path: Path, candidates: tuple[str, ...]) -> list[Path]:
    return [project_path / candidate for candidate in candidates if (project_path / candidate).exists()]


def is_protected_path(route_path: str) -> bool:
    return any(route_path == prefix or route_path.startswith(prefix + "/") for prefix in PROTECTED_PREFIXES)


def _route_from_parts(parts: tuple[str, ...]) -> str:
    public_parts = [part for part in parts if not (part.startswith("(") and part.endswith(")"))]
    if public_parts == ["index"] or not public_parts:
        return "/"
    if public_parts[-1] == "index":
        public_parts = public_parts[:-1]
    return "/" + "/".join(public_parts)


def _has_private_part(parts: tuple[str, ...]) -> bool:
    return any(part.startswith("_") for part in parts)


def _detect_methods(source: Path) -> list[str]:
    text = source.read_text(encoding="utf-8", errors="ignore")
    methods = []
    for method in HTTP_METHODS:
        if re.search(rf"\b(export\s+)?(async\s+)?function\s+{method}\b|\bexport\s+const\s+{method}\b", text):
            methods.append(method)
        elif _uses_req_method(text, method):
            methods.append(method)
    return methods


def _uses_req_method(text: str, method: str) -> bool:
    quoted = rf"['\"]{method}['\"]"
    comparisons = (
        rf"\breq\.method\s*(?:===|!==|==|!=)\s*{quoted}",
        rf"\breq\.method\?\.toUpperCase\(\)\s*(?:===|!==|==|!=)\s*{quoted}",
        rf"\bcase\s+{quoted}\s*:",
    )
    return any(re.search(pattern, text) for pattern in comparisons)
