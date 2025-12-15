from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_tasks_empty():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []

def test_create_task():
    response = client.post("/tasks", json={"title": "Test task", "description": "Description"})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test task"
    assert data["id"] == 1
    assert data["status"] == "pending"

def test_get_task():
    client.post("/tasks", json={"title": "Test task"})
    response = client.get("/tasks/1")
    assert response.status_code == 200
    assert response.json()["id"] == 1

def test_update_task():
    client.post("/tasks", json={"title": "Old title"})
    response = client.put("/tasks/1", json={"title": "New title", "status": "completed"})
    assert response.status_code == 200
    assert response.json()["title"] == "New title"
    assert response.json()["status"] == "completed"

def test_delete_task():
    client.post("/tasks", json={"title": "To delete"})
    response = client.delete("/tasks/1")
    assert response.status_code == 200
    assert response.json() == {"detail": "Task deleted"}
    response = client.get("/tasks/1")
    assert response.status_code == 404

def test_get_nonexistent_task():
    response = client.get("/tasks/999")
    assert response.status_code == 404