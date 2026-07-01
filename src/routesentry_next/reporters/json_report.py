from __future__ import annotations

from ..models import ScanReport, to_plain


def render_json(report: ScanReport) -> dict:
    return to_plain(report)
