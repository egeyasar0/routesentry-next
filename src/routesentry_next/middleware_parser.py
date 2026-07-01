from __future__ import annotations

import re
from pathlib import Path

from .models import MiddlewareInfo


MIDDLEWARE_FILES = (
    "middleware.ts",
    "middleware.js",
    "src/middleware.ts",
    "src/middleware.js",
    "proxy.ts",
    "proxy.js",
    "src/proxy.ts",
    "src/proxy.js",
)


def parse_middleware(project_path: Path) -> MiddlewareInfo:
    for relative in MIDDLEWARE_FILES:
        source = Path(project_path) / relative
        if source.exists():
            text = source.read_text(encoding="utf-8", errors="ignore")
            matchers = _extract_matchers(text)
            return MiddlewareInfo(exists=True, source_file=source, matchers=matchers, broad=not matchers)
    return MiddlewareInfo(exists=False)


def _extract_matchers(text: str) -> list[str]:
    value = re.search(r"matcher\s*:\s*(\[[^\]]*\]|['\"][^'\"]+['\"])", text, re.S)
    if not value:
        return []
    return re.findall(r"['\"]([^'\"]+)['\"]", value.group(1))

