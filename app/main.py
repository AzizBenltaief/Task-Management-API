from fastapi import FastAPI,HTTPException,Body
from pydantic import BaseModel
from typing import List,Optional
import uvicorn

app = FastAPI(title="Task Management API",description="A simple TODO List API",version="1.0")

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


@app.get("/tasks/{task_id}", response_model=Task)
def  get_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            return task
    raise HTTPException(status_code=404,detail = "Task not found")


@app.get("/tasks/filter", response_model=List[Task])
def filter_tasks(status: str):
    return [task for task in tasks if task.status == status]


@app.get("/tasks/search", response_model=List[Task])
def get_tasks_by_title(title: str):
    return [task for task in tasks if title.lower() in task.title.lower()]





@app.patch("/tasks/{task_id}/complete", response_model=Task)
def complete_task(task_id: int):
    for task in tasks:
        if task.id == task_id:
            task.status = "completed"
            return task
    raise HTTPException(status_code=404, detail="Task not found")


@app.post("/tasks", response_model = Task)
def create_task(task: TaskCreate = Body(...)):
    global task_id_counter
    new_task = Task(id=task_id_counter,**task.dict())
    tasks.append(new_task)
    task_id_counter += 1 
    return new_task


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


