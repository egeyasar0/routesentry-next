from pathlib import Path

from routesentry_next.analyzer import scan_project
from routesentry_next.reporters.json_report import render_json
from routesentry_next.reporters.markdown import render_markdown
from routesentry_next.reporters.sarif import render_sarif


FIXTURES = Path(__file__).parent / "fixtures"


def test_json_report_contains_schema_score_and_findings():
    report = scan_project(FIXTURES / "middleware_only_app")
    data = render_json(report)

    assert data["schema_version"] == "1.0"
    assert data["score"] == 85
    assert data["findings"][0]["rule_id"] == "RSN-001"


def test_markdown_report_names_limitations_and_findings():
    report = scan_project(FIXTURES / "matcher_miss_app")
    markdown = render_markdown(report)

    assert "## Limitations" in markdown
    assert "RSN-002" in markdown
    assert "no route-level authorization pattern was detected" in markdown


def test_sarif_report_contains_required_finding_fields():
    report = scan_project(FIXTURES / "middleware_only_app")
    sarif = render_sarif(report)
    run = sarif["runs"][0]
    result = run["results"][0]
    properties = result["properties"]

    assert sarif["version"] == "2.1.0"
    assert run["tool"]["driver"]["name"] == "RouteSentry Next"
    assert result["ruleId"] == "RSN-001"
    assert result["locations"][0]["physicalLocation"]["artifactLocation"]["uri"].endswith("route.ts")
    assert properties["confidence"] == "high"
    assert "Add route-level session/role validation" in properties["recommendation"]
