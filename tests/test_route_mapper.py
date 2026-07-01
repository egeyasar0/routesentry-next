from pathlib import Path

from routesentry_next.route_mapper import map_routes


FIXTURES = Path(__file__).parent / "fixtures"


def test_maps_app_route_handler_with_methods():
    routes = map_routes(FIXTURES / "mutation_without_auth_app")

    route = next(route for route in routes if route.path == "/api/profile")
    assert route.route_type == "route_handler"
    assert route.router == "app"
    assert route.http_methods == ["POST"]


def test_maps_public_app_page_and_health_route():
    routes = map_routes(FIXTURES / "safe_public_app")
    paths = {route.path for route in routes}

    assert "/" in paths
    assert "/api/health" in paths


def test_maps_src_app_and_pages_layouts():
    routes = map_routes(FIXTURES / "src_layout_app")
    by_path = {route.path: route for route in routes}

    assert by_path["/dashboard"].router == "app"
    assert by_path["/users/[id]"].route_type == "page"
    assert by_path["/docs/[...slug]"].route_type == "page"
    assert by_path["/settings"].router == "pages"
    assert by_path["/api/account"].route_type == "api_route"
    assert by_path["/api/admin/users"].route_type == "route_handler"
    assert "/_components" not in by_path


def test_detects_pages_api_req_method_mutation():
    routes = map_routes(FIXTURES / "pages_api_method_app")
    route = next(route for route in routes if route.path == "/api/account")

    assert route.route_type == "api_route"
    assert route.http_methods == ["POST"]
