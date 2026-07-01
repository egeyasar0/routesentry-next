from .models import Finding


POINTS = {"HIGH": 15, "MEDIUM": 8, "LOW": 3, "INFO": 0}


def score(findings: list[Finding]) -> int:
    return max(0, 100 - sum(POINTS[finding.severity] for finding in findings))

