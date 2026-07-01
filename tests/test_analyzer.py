from pathlib import Path

from routesentry_next.analyzer import looks_like_next_project, scan_project


FIXTURES = Path(__file__).parent / "fixtures"


def finding_ids(project_name: str) -> set[str]:
    report = scan_project(FIXTURES / project_name)
    return {finding.rule_id for finding in report.findings}


def test_middleware_only_app_reports_rsn_001_high():
    report = scan_project(FIXTURES / "middleware_only_app")

    assert [(finding.rule_id, finding.severity) for finding in report.findings] == [("RSN-001", "HIGH")]
    assert report.routes[0].risk_status == "middleware_only"


def test_matcher_miss_app_reports_rsn_002_high():
    assert finding_ids("matcher_miss_app") == {"RSN-002"}


def test_route_level_auth_app_has_no_mvp_findings_for_route():
    assert finding_ids("route_level_auth_app") == set()


def test_mutation_without_auth_app_reports_rsn_003_high():
    assert finding_ids("mutation_without_auth_app") == {"RSN-003"}


def test_safe_public_app_has_no_high_findings():
    report = scan_project(FIXTURES / "safe_public_app")

    assert report.findings == []
    assert report.summary["high"] == 0


def test_src_layout_project_is_detected_and_scanned():
    report = scan_project(FIXTURES / "src_layout_app")

    assert looks_like_next_project(FIXTURES / "src_layout_app") is True
    assert {route.path for route in report.routes} >= {"/dashboard", "/api/admin/users", "/api/account"}


def test_pages_api_method_mutation_reports_rsn_003_high():
    report = scan_project(FIXTURES / "pages_api_method_app")

    assert [(finding.rule_id, finding.severity) for finding in report.findings] == [("RSN-003", "HIGH")]


def test_cors_authorization_header_mutation_still_reports_rsn_003():
    report = scan_project(FIXTURES / "cors_authorization_header_app")

    assert [(finding.rule_id, finding.severity) for finding in report.findings] == [("RSN-003", "HIGH")]
