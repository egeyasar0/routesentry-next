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


def test_cors_authorization_allow_header_is_not_auth():
    route_file = FIXTURES / "cors_authorization_header_app" / "app" / "api" / "profile" / "route.ts"

    result = detect_route_auth(route_file)
    assert result.has_route_level_auth is False
    assert result.status == "auth_not_detected"


def test_detects_res_status_401_branch():
    route_file = FIXTURES / "pages_api_res_status_auth_app" / "pages" / "api" / "account.ts"

    assert detect_route_auth(route_file).has_route_level_auth is True


def test_detects_cookie_auth_patterns_with_single_and_double_quotes():
    route_file = FIXTURES / "cookie_auth_patterns_app" / "app" / "api" / "admin" / "users" / "route.ts"

    result = detect_route_auth(route_file)
    assert result.has_route_level_auth is True
    assert 'cookies().get("session")' in result.patterns
    assert "cookies().get('auth')" in result.patterns
