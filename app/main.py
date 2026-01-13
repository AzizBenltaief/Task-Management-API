from fastapi import FastAPI,HTTPException,Body,Request, Response
from pydantic import BaseModel
from typing import List,Optional
import uvicorn
import logging
import json
import time
from starlette.middleware.base import BaseHTTPMiddleware

# Observability imports
from prometheus_fastapi_instrumentator import Instrumentator
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

# Structured JSON logging
class JSONLogFormatter(logging.Formatter):
    def format(self, record):
        log_record = {
            "timestamp": self.formatTime(record, "%Y-%m-%dT%H:%M:%S%z"),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "line": record.lineno,
        }
        if hasattr(record, "request_info"):
            log_record.update(record.request_info)
        if record.exc_info:
            log_record["exc_info"] = self.formatException(record.exc_info)
        return json.dumps(log_record)

# Configure Uvicorn loggers for JSON
logging.getLogger("uvicorn.access").handlers = [logging.StreamHandler()]
logging.getLogger("uvicorn.access").propagate = False
for logger_name in ["uvicorn", "uvicorn.access", "uvicorn.error"]:
    logger = logging.getLogger(logger_name)
    logger.handlers.clear()
    handler = logging.StreamHandler()
    handler.setFormatter(JSONLogFormatter())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

app = FastAPI(
    title="Task Management API",
    description="A simple TODO List API",
    version="1.0"
)

# Security Headers Middleware
class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response: Response = await call_next(request)
        
        # Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # Spectre vulnerability mitigation
        response.headers["Cross-Origin-Embedder-Policy"] = "require-corp"
        response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
        response.headers["Cross-Origin-Resource-Policy"] = "same-origin"
        
        # Additional security headers (bonus)
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        
        return response

# Add the middleware
app.add_middleware(SecurityHeadersMiddleware)
# Prometheus metrics
Instrumentator(should_group_status_codes=False).instrument(app).expose(app, endpoint="/metrics")

# OpenTelemetry tracing (console exporter for easy evidence)
trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
FastAPIInstrumentor.instrument_app(app)

# Middleware for structured request logs
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    request_info = {
        "method": request.method,
        "url": str(request.url),
        "status_code": response.status_code,
        "duration_ms": round(duration * 1000, 2),
        "client_ip": request.client.host if request.client else None,
    }
    logging.getLogger("uvicorn.access").info("HTTP request", extra={"request_info": request_info})
    return response


tasks = []
task_id_counter = 1

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str = "pending"

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str = "pending"

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[str] = None


@app.get("/")
def root():
    return {"message": " Welcome to the Task Management API !"}


@app.get("/tasks",response_model=List[Task])
def get_tasks():
    return tasks


@app.get("/tasks/summary")
def task_stats():
    return {
        "total_tasks":len(tasks),
        "pending_tasks":len([task for task in tasks if task.status == "pending"]),
        "completed_tasks": len([task for task in tasks if task.status == "completed"])
    }


@app.get("/tasks/filter", response_model=List[Task])
def filter_tasks(status: Optional[str] = None):  
    if status is None:
        raise HTTPException(status_code=400, detail="Query parameter 'status' is required")
    return [task for task in tasks if task.status == status]


@app.get("/tasks/search", response_model=List[Task])
def get_tasks_by_title(title: Optional[str] = None):  
    if title is None:
        raise HTTPException(status_code=400, detail="Query parameter 'title' is required")
    return [task for task in tasks if title.lower() in task.title.lower()]

@app.get("/tasks/{task_id}", response_model=Task)
def  get_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404,detail = "Task not found")


@app.post("/tasks", response_model=Task)
def create_task(task: TaskCreate = Body(...)):
    global task_id_counter
    new_task = Task(id=task_id_counter, **task.model_dump()) 
    tasks.append(new_task)
    task_id_counter += 1 
    return new_task


@app.patch("/tasks/{task_id}/complete", response_model=Task)
def complete_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            task.status = "completed"
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.put("/tasks/{task_id}", response_model = Task)
def update_task(task_id: int, update_data: TaskUpdate = Body(...)):
    for task in tasks:
        if task.id == task_id:
            if update_data.title is not None:
                task.title = update_data.title
            if update_data.description is not None:
                task.description = update_data.description
            if update_data.status is not None:
                task.status = update_data.status
            return task
    raise HTTPException(status_code = 404, detail=f"Task not found with id : {task_id}")


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    global tasks
    for i, task in enumerate(tasks):
        if task.id == task_id:
            del tasks[i]
            return {"detail": "Task deleted"}  
    raise HTTPException(status_code=404, detail="Task not found")


@app.delete("/tasks")
def delete_all_tasks():
    global tasks, task_id_counter
    tasks.clear()
    task_id_counter = 1
    return {"detail": " All tasks have been deleted successfully !"}


if __name__ == "__main__":
    uvicorn.run(app,host = "localhost",port = 9000)


