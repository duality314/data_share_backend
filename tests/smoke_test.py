import pytest

from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.testing = True
    return app


def test_health_endpoint(app):
    client = app.test_client()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.get_json() == {"ok": True}


def test_routes_registered(app):
    rules = [r.rule for r in app.url_map.iter_rules()]
    # 验证关键路由已注册（允许使用前缀匹配）
    assert any(r.startswith("/api/auth") for r in rules)
    assert any(r.startswith("/api/datasets") for r in rules)
    assert any(r.startswith("/api/shares") for r in rules)


def test_auth_endpoints_validate_input(app):
    client = app.test_client()
    # 发送空载荷应返回验证错误（400/422）而不是 500
    r1 = client.post("/api/auth/register", json={})
    assert r1.status_code in (400, 422)

    r2 = client.post("/api/auth/login", json={})
    assert r2.status_code in (400, 422)


def test_protected_endpoints_require_auth(app):
    client = app.test_client()
    # 未携带 JWT 的关键受保护路由应返回 401
    r = client.post("/api/datasets", json={})
    assert r.status_code == 401

    r = client.get("/api/datasets/mine")
    assert r.status_code == 401

    r = client.get("/api/datasets/1/download")
    assert r.status_code == 401

    r = client.get("/api/shares/sharing-with-others")
    assert r.status_code == 401
