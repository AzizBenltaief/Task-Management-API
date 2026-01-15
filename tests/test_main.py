from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "Welcome" in response.json()["message"]

def test_get_tasks_empty():
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []

def test_create_task():
    response = client.post("/tasks", json={"title": "Test task"})
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
    client.post("/tasks", json={"title": "Old"})
    response = client.put("/tasks/1", json={"title": "New", "status": "completed"})
    assert response.status_code == 200
    assert response.json()["title"] == "New"
    assert response.json()["status"] == "completed"

def test_delete_task():
    client.post("/tasks", json={"title": "To delete"})
    response = client.delete("/tasks/1")
    assert response.status_code == 200
    assert response.json() == {"detail": "Task deleted"}
    response = client.get("/tasks/1")
    assert response.status_code == 404

# Nouveaux tests pour tes endpoints ajoutés
def test_task_summary_empty():
    client.delete("/tasks")  
    response = client.get("/tasks/summary")
    assert response.status_code == 200
    assert response.json() == {"total_tasks": 0, "pending_tasks": 0, "completed_tasks": 0}

def test_task_summary_with_data():
    client.delete("/tasks")
    client.post("/tasks", json={"title": "Pending"})
    client.post("/tasks", json={"title": "Completed", "status": "completed"})
    response = client.get("/tasks/summary")
    assert response.status_code == 200
    assert response.json()["total_tasks"] == 2
    assert response.json()["pending_tasks"] == 1
    assert response.json()["completed_tasks"] == 1

def test_filter_tasks():
    client.delete("/tasks")
    client.post("/tasks", json={"title": "P1", "status": "pending"})
    client.post("/tasks", json={"title": "C1", "status": "completed"})
    response = client.get("/tasks/filter?status=pending")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["status"] == "pending"

def test_search_tasks_by_title():
    client.delete("/tasks")
    client.post("/tasks", json={"title": "Buy milk"})
    client.post("/tasks", json={"title": "Buy bread"})
    response = client.get("/tasks/search?title=milk")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert "milk" in response.json()[0]["title"].lower()

def test_complete_task():
    client.delete("/tasks")
    client.post("/tasks", json={"title": "To complete"})
    response = client.patch("/tasks/1/complete")
    assert response.status_code == 200
    assert response.json()["status"] == "completed"

def test_delete_all_tasks():
    client.post("/tasks", json={"title": "One"})
    client.post("/tasks", json={"title": "Two"})
    response = client.delete("/tasks")
    assert response.status_code == 200
    assert "All tasks have been deleted" in response.json()["detail"]
    response = client.get("/tasks")
    assert response.json() == []

def test_get_nonexistent_task():
    client.delete("/tasks")
    response = client.get("/tasks/999")
    assert response.status_code == 404