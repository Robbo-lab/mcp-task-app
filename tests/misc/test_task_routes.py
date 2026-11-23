from fastapi.testclient import TestClient

from main import app

HTTP_OK = 200
HTTP_NOT_FOUND = 404


def test_get_task_by_name_not_found():
    client = TestClient(app)

    response = client.get("/tasks/by-name/NonExistentTask")
    assert response.status_code == HTTP_NOT_FOUND


def test_get_task_by_id_not_found():
    client = TestClient(app)

    response = client.get("/tasks/999999")
    assert response.status_code == HTTP_NOT_FOUND


def test_list_tasks():
    client = TestClient(app)

    response = client.get("/tasks")
    assert response.status_code == HTTP_OK
    assert isinstance(response.json(), list)


def test_post_route_exists():
    routes = [
        (route.path, route.methods) for route in app.routes if hasattr(route, "methods")
    ]

    assert any(path == "/tasks" and "POST" in methods for path, methods in routes)


def test_delete():
    routes = [
        (route.path, route.methods) for route in app.routes if hasattr(route, "methods")
    ]

    assert any(
        path == "/tasks/by-name/{name}" and "DELETE" in methods
        for path, methods in routes
    )


def test_complete_tasks():
    routes = [
        (route.path, route.methods) for route in app.routes if hasattr(route, "methods")
    ]

    assert any(
        path == "/tasks/by-name/{name}/complete" and "PATCH" in methods
        for path, methods in routes
    )
