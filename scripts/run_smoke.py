#!/usr/bin/env python3
"""Simple smoke test runner that uses the Flask test client.
This avoids relying on pytest being installed in the environment.
"""
import sys
from pathlib import Path

# Ensure project root is on sys.path so `from app import create_app` works
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from app import create_app


def assert_ok(cond, msg, failures):
    if not cond:
        print("FAIL:", msg)
        failures.append(msg)
    else:
        print("OK:", msg)


def main():
    app = create_app()
    app.testing = True
    client = app.test_client()
    failures = []

    # health
    r = client.get("/health")
    assert_ok(r.status_code == 200 and r.get_json() == {"ok": True}, 
              "/health returns 200 and {'ok': True}", failures)

    # routes registered
    rules = [r.rule for r in app.url_map.iter_rules()]
    assert_ok(any(r.startswith("/api/auth") for r in rules), "auth routes registered", failures)
    assert_ok(any(r.startswith("/api/datasets") for r in rules), "datasets routes registered", failures)
    assert_ok(any(r.startswith("/api/shares") for r in rules), "shares routes registered", failures)

    # auth validation
    r = client.post("/api/auth/register", json={})
    assert_ok(r.status_code in (400, 422), "/api/auth/register validates missing payload", failures)

    r = client.post("/api/auth/login", json={})
    assert_ok(r.status_code in (400, 422), "/api/auth/login validates missing payload", failures)

    # protected endpoints require auth
    r = client.post("/api/datasets", json={})
    assert_ok(r.status_code == 401, "/api/datasets requires auth", failures)

    r = client.get("/api/datasets/mine")
    assert_ok(r.status_code == 401, "/api/datasets/mine requires auth", failures)

    r = client.get("/api/datasets/1/download")
    assert_ok(r.status_code == 401, "/api/datasets/<id>/download requires auth", failures)

    r = client.get("/api/shares/sharing-with-others")
    assert_ok(r.status_code == 401, "/api/shares/sharing-with-others requires auth", failures)

    print("\nSummary: {} failures".format(len(failures)))
    if failures:
        sys.exit(2)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
