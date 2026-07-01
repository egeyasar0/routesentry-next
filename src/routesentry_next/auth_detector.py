from __future__ import annotations

import re
from pathlib import Path

from .models import AuthDetection


PATTERNS = (
    "auth()",
    "getServerSession(",
    "unstable_getServerSession(",
    "getToken(",
    "currentUser(",
    "auth.protect(",
    "clerkClient",
    "createServerClient(",
    "createRouteHandlerClient(",
    "getUser(",
    "getSession(",
    "requireAuth(",
    "requireUser(",
    "requireAdmin(",
    "withAuth(",
    "verifySession(",
    "verifyAuth(",
    "validateSession(",
    'cookies().get("session")',
    'cookies().get("auth")',
    'headers().get("authorization")',
    "Authorization",
)

IMPORT_AWARE_NAMES = (
    "requireAuth",
    "requireAdmin",
    "withAuth",
    "auth",
    "getServerSession",
    "currentUser",
    "createServerClient",
)


def detect_route_auth(source: Path) -> AuthDetection:
    text = Path(source).read_text(encoding="utf-8", errors="ignore")
    found = [pattern for pattern in PATTERNS if pattern.lower() in text.lower()]
    imported = _imported_auth_names(text)
    for pattern, local_name in imported.items():
        if re.search(rf"\b{re.escape(local_name)}\s*\(", text):
            found.append(pattern)

    if re.search(r"\bbearer\b", text, re.I):
        found.append("bearer token checks")
    if re.search(r"\bstatus\s*:\s*40[13]\b", text):
        found.append("401/403 response branch")

    if found:
        return AuthDetection(True, "route_level_auth_detected", found)
    if imported:
        return AuthDetection(False, "manual_review", list(imported))
    return AuthDetection(False, "auth_not_detected", found)


def _imported_auth_names(text: str) -> dict[str, str]:
    imported: dict[str, str] = {}
    for body in re.findall(r"import\s*\{([^}]+)\}\s*from\s*['\"][^'\"]+['\"]", text):
        for item in body.split(","):
            parts = item.strip().split()
            if not parts:
                continue
            original = parts[0]
            if original in IMPORT_AWARE_NAMES:
                local = parts[2] if len(parts) == 3 and parts[1] == "as" else original
                imported[item.strip()] = local
    for local in re.findall(r"import\s+([A-Za-z_$][\w$]*)\s+from\s*['\"][^'\"]+['\"]", text):
        if local in IMPORT_AWARE_NAMES:
            imported[local] = local
    return imported
