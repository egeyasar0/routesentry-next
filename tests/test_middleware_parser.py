from pathlib import Path

from routesentry_next.middleware_parser import parse_middleware


FIXTURES = Path(__file__).parent / "fixtures"


def test_array_matcher_covers_matching_route_only():
    middleware = parse_middleware(FIXTURES / "matcher_miss_app")

    assert middleware.exists is True
    assert middleware.covers("/dashboard") is True
    assert middleware.covers("/dashboard/settings") is True
    assert middleware.covers("/api/admin/users") is False


def test_no_middleware_reports_absent():
    middleware = parse_middleware(FIXTURES / "safe_public_app")

    assert middleware.exists is False
    assert middleware.covers("/api/health") is False


def test_broad_middleware_covers_routes_without_matcher():
    middleware = parse_middleware(FIXTURES / "broad_middleware_app")

    assert middleware.exists is True
    assert middleware.broad is True
    assert middleware.covers("/api/admin/users") is True


def test_src_middleware_array_matcher_is_parsed():
    middleware = parse_middleware(FIXTURES / "src_middleware_app")

    assert middleware.source_file.name == "middleware.ts"
    assert middleware.covers("/api/admin/users") is True
    assert middleware.covers("/account") is True
    assert middleware.covers("/billing") is False


def test_matcher_missing_api_admin_coverage_stays_false():
    middleware = parse_middleware(FIXTURES / "missing_api_coverage_app")

    assert middleware.covers("/dashboard") is True
    assert middleware.covers("/api/admin/users") is False
