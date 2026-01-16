# Task Management API

A lightweight REST API for managing tasks with full DevOps implementation including CI/CD, observability, security scanning, and Kubernetes deployment.

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Local Development](#local-development)
- [Docker Usage](#docker-usage)
- [Kubernetes Deployment](#kubernetes-deployment)
- [API Documentation](#api-documentation)
- [Observability](#observability)
- [Security](#security)
- [CI/CD Pipeline](#cicd-pipeline)

## ✨ Features

- ✅ RESTful API with CRUD operations for task management
- ✅ FastAPI framework with automatic OpenAPI documentation
- ✅ Structured JSON logging
- ✅ Prometheus metrics integration
- ✅ OpenTelemetry distributed tracing
- ✅ Docker containerization
- ✅ Kubernetes deployment with auto-scaling
- ✅ CI/CD pipeline with GitHub Actions
- ✅ Security scanning (SAST with Bandit, DAST with OWASP ZAP)

## 🛠️ Tech Stack

- **Framework**: FastAPI 0.115.12
- **Language**: Python 3.11
- **Containerization**: Docker
- **Orchestration**: Kubernetes
- **CI/CD**: GitHub Actions
- **Observability**: 
  - Metrics: Prometheus via `prometheus-fastapi-instrumentator`
  - Logging: Structured JSON logs
  - Tracing: OpenTelemetry
- **Security**: 
  - SAST: Bandit
  - DAST: OWASP ZAP
- **Testing**: pytest, httpx

## 📦 Prerequisites

- Python 3.11+
- Docker & Docker Desktop (with Kubernetes enabled)
- kubectl
- Git

## 🚀 Local Development

### 1. Clone the repository

```bash
git clone https://github.com/AzizBenltaief/Task-Management-API.git
cd Task-Management-API
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the application

```bash
# Option 1: Using uvicorn directly
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Option 2: Using Python
python -m uvicorn app.main:app --reload
```

### 4. Access the API

- **API Base URL**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Metrics**: http://localhost:8000/metrics

### 5. Run tests

```bash
pytest tests/ -v
```

## 🐳 Docker Usage

### Build the Docker image

```bash
docker build -t task-api:latest .
```

### Run with Docker

```bash
docker run -d -p 8000:8000 --name task-api task-api:latest
```

### Using Docker Compose

```bash
# Start the application
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the application
docker-compose down
```

### Push to Docker Hub

```bash
docker tag task-api:latest <your-username>/task-management-api:latest
docker push <your-username>/task-management-api:latest
```

## ☸️ Kubernetes Deployment

### Prerequisites

Enable Kubernetes in Docker Desktop:
- Open Docker Desktop → Settings → Kubernetes → Enable Kubernetes

### Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f k8s/

# Check deployment status
kubectl get all -l app=task-management-api

# View pods
kubectl get pods -l app=task-management-api

# View services
kubectl get svc task-management-api-service
```

### Access the application

```bash
# The service is exposed on NodePort 30080
# Access at: http://localhost:30080

# Or use port-forward
kubectl port-forward service/task-management-api-service 8080:80
# Access at: http://localhost:8080
```

### Scale the deployment

```bash
# Manual scaling
kubectl scale deployment task-management-api --replicas=5

# Auto-scaling is configured via HPA (2-10 replicas based on CPU/Memory)
kubectl get hpa
```

### View logs

```bash
# Get pod name
kubectl get pods -l app=task-management-api

# View logs
kubectl logs <pod-name>

# Follow logs
kubectl logs -f <pod-name>
```

### Clean up

```bash
kubectl delete -f k8s/
```

## 📖 API Documentation

### Endpoints

#### 1. Welcome Message
```http
GET /
```
**Response:**
```json
{
  "message": "Welcome to the Task Management API!"
}
```

#### 2. Get All Tasks
```http
GET /tasks
```
**Response:**
```json
[
  {
    "id": 1,
    "title": "Complete project",
    "description": "Finish the DevOps project",
    "status": "pending"
  }
]
```

#### 3. Create Task
```http
POST /tasks
Content-Type: application/json

{
  "title": "New task",
  "description": "Task description",
  "status": "pending"
}
```

#### 4. Get Task by ID
```http
GET /tasks/{task_id}
```

#### 5. Update Task
```http
PUT /tasks/{task_id}
Content-Type: application/json

{
  "title": "Updated title",
  "description": "Updated description",
  "status": "completed"
}
```

#### 6. Complete Task
```http
PATCH /tasks/{task_id}/complete
```

#### 7. Delete Task
```http
DELETE /tasks/{task_id}
```

#### 8. Delete All Tasks
```http
DELETE /tasks
```

#### 9. Get Task Statistics
```http
GET /tasks/summary
```
**Response:**
```json
{
  "total_tasks": 5,
  "pending_tasks": 3,
  "completed_tasks": 2
}
```

#### 10. Filter Tasks by Status
```http
GET /tasks/filter?status=pending
```

#### 11. Search Tasks by Title
```http
GET /tasks/search?title=project
```

### API Examples with curl

```bash
# Create a task
curl -X POST http://localhost:8000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","description":"Milk, eggs, bread","status":"pending"}'

# Get all tasks
curl http://localhost:8000/tasks

# Get task by ID
curl http://localhost:8000/tasks/1

# Update task
curl -X PUT http://localhost:8000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy groceries","status":"completed"}'

# Complete task
curl -X PATCH http://localhost:8000/tasks/1/complete

# Delete task
curl -X DELETE http://localhost:8000/tasks/1

# Get statistics
curl http://localhost:8000/tasks/summary

# Filter by status
curl http://localhost:8000/tasks/filter?status=pending

# Search by title
curl http://localhost:8000/tasks/search?title=grocery
```

## 📊 Observability

### Metrics

Prometheus metrics are exposed at `/metrics`:

```bash
curl http://localhost:8000/metrics
```

**Available metrics:**
- Request count
- Request duration
- Response status codes
- Active requests

### Logs

Structured JSON logs for all requests:

```json
{
  "timestamp": "2026-01-13T12:00:00+0100",
  "level": "INFO",
  "message": "Request processed",
  "module": "main",
  "line": 45,
  "method": "GET",
  "path": "/tasks",
  "status_code": 200,
  "duration_ms": 2.5
}
```

View logs in Docker:
```bash
docker logs task-api -f
```

View logs in Kubernetes:
```bash
kubectl logs -f <pod-name>
```

### Tracing

OpenTelemetry tracing is integrated for distributed tracing:
- Automatic span creation for each request
- Request/response tracking
- Error tracking

## 🔒 Security

### SAST (Static Application Security Testing)

**Tool**: Bandit

Runs automatically in CI/CD pipeline to scan for:
- Security vulnerabilities in Python code
- Common security issues
- Hardcoded secrets
- Unsafe practices

Run locally:
```bash
pip install bandit
bandit -r app/ -f json -o bandit-report.json
```

### DAST (Dynamic Application Security Testing)

**Tool**: OWASP ZAP

Runs API security scans against the running application to detect:
- API vulnerabilities
- Authentication issues
- Injection attacks
- Security misconfigurations

The scan runs automatically in the CI/CD pipeline.

### Security Best Practices

- ✅ No hardcoded secrets
- ✅ Input validation with Pydantic
- ✅ HTTP security headers
- ✅ Regular dependency updates
- ✅ Minimal Docker image (Python slim)
- ✅ Non-root user in container
- ✅ Vulnerability scanning in CI/CD

## 🔄 CI/CD Pipeline

The project uses **GitHub Actions** for automated CI/CD with the following stages:

### Pipeline Stages

1. **Tests** 🧪
   - Run pytest suite
   - Verify all endpoints
   - Check code coverage

2. **SAST Scan** 🔍
   - Bandit security scan
   - Report vulnerabilities
   - Upload artifacts

3. **DAST Scan** 🛡️
   - Start application
   - Run OWASP ZAP scan
   - Upload security reports

4. **Docker Build & Push** 🐳
   - Build Docker image
   - Push to Docker Hub
   - Tag with latest

### Workflow File

See `.github/workflows/ci-cd.yml` for the complete pipeline configuration.

### GitHub Secrets Required

Configure these secrets in your GitHub repository:

- `DOCKER_USERNAME`: Your Docker Hub username
- `DOCKER_PASSWORD`: Your Docker Hub password/token

### Trigger Events

- **Push to main**: Full pipeline execution
- **Pull requests**: Tests and security scans
- **Manual**: Can be triggered via GitHub Actions UI

## 📁 Project Structure

```
Task-Management-API/
├── .github/
│   └── workflows/
│       └── ci-cd.yml          # CI/CD pipeline
├── app/
│   ├── __init__.py
│   └── main.py                # FastAPI application
├── tests/
│   ├── __init__.py
│   └── test_main.py           # Test suite
├── k8s/
│   ├── deployment.yaml        # Kubernetes deployment
│   └── service.yaml           # Kubernetes service
├── Dockerfile                 # Docker image definition
├── docker-compose.yml         # Docker Compose configuration
├── requirements.txt           # Python dependencies
├── openapi.json              # OpenAPI specification
└── README.md                 # This file
```

## 🧪 Testing

### Run all tests

```bash
pytest tests/ -v
```

### Run with coverage

```bash
pytest tests/ -v --cov=app --cov-report=html
```

### Test specific endpoint

```bash
pytest tests/test_main.py::test_read_root -v
```

## 🤝 Contributing

1. Create a GitHub Issue for your task
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes
4. Run tests: `pytest tests/`
5. Commit: `git commit -m "Add feature"`
6. Push: `git push origin feature/your-feature`
7. Open a Pull Request
8. Request peer review

## 📄 License

This project is part of a DevOps course assignment.

## 👨‍💻 Author

**Aziz Ben Ltaief**
- GitHub: [@AzizBenltaief](https://github.com/AzizBenltaief)

## 🎯 Project Checklist

- ✅ Backend API (under 150 lines of core code)
- ✅ GitHub Issues and Projects for task management
- ✅ Git version control with meaningful commits
- ✅ Pull Requests with peer reviews
- ✅ CI/CD pipeline (build, test, deploy)
- ✅ Observability (metrics, logs, tracing)
- ✅ Security scans (SAST + DAST)
- ✅ Docker containerization
- ✅ Docker Compose configuration
- ✅ Kubernetes deployment manifests
- ✅ Published Docker image on Docker Hub
- ✅ Comprehensive documentation
- ✅ API examples and usage guide

---

**Made with ❤️ for DevOps Course 2026**
