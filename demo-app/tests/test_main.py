from fastapi.testclient import TestClient

from demo_app import create_app


def _client() -> TestClient:
    return TestClient(create_app())


class TestHealthz:
    def test_returns_ok(self) -> None:
        response = _client().get("/healthz")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestGreet:
    def test_greets_a_valid_name(self) -> None:
        response = _client().post("/greet", json={"name": "Ada"})
        assert response.status_code == 200
        assert response.json() == {"message": "Hello, Ada!"}

    def test_rejects_a_name_with_digits(self) -> None:
        response = _client().post("/greet", json={"name": "Ada123"})
        assert response.status_code == 422

    def test_rejects_a_name_with_script_injection_characters(self) -> None:
        response = _client().post("/greet", json={"name": "<script>alert(1)</script>"})
        assert response.status_code == 422

    def test_rejects_an_empty_name(self) -> None:
        response = _client().post("/greet", json={"name": ""})
        assert response.status_code == 422


class TestVersion:
    def test_returns_the_version(self) -> None:
        response = _client().get("/version")
        assert response.status_code == 200
        assert response.json() == {"version": "1.0.0"}
