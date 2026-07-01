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
    found.extend(_request_auth_patterns(text))
    imported = _imported_auth_names(text)
    for pattern, local_name in imported.items():
        if re.search(rf"\b{re.escape(local_name)}\s*\(", text):
            found.append(pattern)

    if re.search(r"\bbearer\b", text, re.I) and _has_authorization_header_access(text):
        found.append("bearer token checks")
    if re.search(r"\bstatus\s*:\s*40[13]\b", text):
        found.append("401/403 response branch")
    if re.search(r"\b(?:res|response)\.status\(\s*40[13]\s*\)", text):
        found.append("401/403 response branch")

    if found:
        return AuthDetection(True, "route_level_auth_detected", found)
    if imported:
        return AuthDetection(False, "manual_review", list(imported))
    return AuthDetection(False, "auth_not_detected", found)


def _request_auth_patterns(text: str) -> list[str]:
    found: list[str] = []
    for match in re.finditer(r"cookies\(\)\.get\(\s*(['\"])(session|auth)\1\s*\)", text):
        found.append(f"cookies().get({match.group(1)}{match.group(2)}{match.group(1)})")
    if _has_authorization_header_access(text):
        found.append("authorization request header")
    return found


def _has_authorization_header_access(text: str) -> bool:
    patterns = (
        r"\b(?:headers\(\)|request\.headers|req\.headers)\.get\(\s*['\"]authorization['\"]\s*\)",
        r"\breq\.headers\.authorization\b",
        r"\breq\.headers\[\s*['\"]authorization['\"]\s*\]",
    )
    return any(re.search(pattern, text, re.I) for pattern in patterns)


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
