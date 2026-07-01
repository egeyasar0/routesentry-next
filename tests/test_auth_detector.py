from pathlib import Path

from routesentry_next.auth_detector import detect_route_auth


FIXTURES = Path(__file__).parent / "fixtures"


def test_detects_route_level_auth_pattern():
    route_file = FIXTURES / "route_level_auth_app" / "app" / "api" / "admin" / "users" / "route.ts"

    assert detect_route_auth(route_file).has_route_level_auth is True


def test_missing_auth_pattern_is_reported_without_overclaiming():
    route_file = FIXTURES / "middleware_only_app" / "app" / "api" / "admin" / "users" / "route.ts"

    result = detect_route_auth(route_file)
    assert result.has_route_level_auth is False
    assert result.status == "auth_not_detected"


def test_detects_imported_auth_wrapper_called_through_alias():
    route_file = FIXTURES / "imported_auth_wrapper_app" / "app" / "api" / "admin" / "users" / "route.ts"

    result = detect_route_auth(route_file)
    assert result.has_route_level_auth is True
    assert "requireAdmin as guard" in result.patterns


def test_imported_auth_wrapper_not_called_is_manual_review():
    route_file = FIXTURES / "uncertain_import_auth_app" / "app" / "api" / "admin" / "users" / "route.ts"

    result = detect_route_auth(route_file)
    assert result.has_route_level_auth is False
    assert result.status == "manual_review"
