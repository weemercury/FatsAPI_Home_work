import logging
from fastapi import FastAPI, Request

from typing import Optional
from pydantic import BaseModel, EmailStr

from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates

app = FastAPI()
templates = Jinja2Templates(directory="templates")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str


tasks = [
   {"id": 1, "title": "Cleaning", "description": "The best Cleaning!", "status": "done"},
   {"id": 2, "title": "Draw", "description": "My new tatoo", "status": "todo"},
   {"id": 3, "title": "Repair my table", "description": "My poor table", "status": "in progress"}
]


@app.get('/')
async def main_root():
    logger.info('Обработал GET запрос.')
    return {'API': 'Tasks'}



@app.get('/tasks')
async def get_tasks():
    logger.info('Обработал GET запрос.')
    return tasks


@app.get("/get_tasks", response_class=HTMLResponse)
async def read_tasks(request: Request):
    return templates.TemplateResponse("tasks.html", {"request": request, "tasks": tasks})


@app.get('/tasks/{task_id}')
async def get_task(task_id: int):
    logger.info('Обработал GET запрос.')
    for task in tasks:
        if task['id'] == task_id:
            return {"task_id": task_id, 'task': task}
    return {'response': "task_id Not found!"}



@app.post("/create_task")
async def create_task(task: Task):       
    logger.info('Отработал POST запрос.')
    tasks.append(task)
    return tasks                           


@app.put("/change_task")
async def change_task(task: Task):
    logger.info(f'Отработал PUT запрос для task = {task}.')
    for t in tasks:
        if t["id"] == task.id:
            t["title"] = task.title
            t["description"] = task.description
            t["status"] = task.status
            return tasks
    return {'response': "task_id Not found!"}


@app.delete("/delete_task/{task_id}")
async def delete_task(task_id: int):
    logger.info(f'Отработал DELETE запрос для task id = {task_id}.')
    for i in range(len(tasks)):
        if tasks[i]["id"] == task_id:
            del tasks[i]
            return {"task_deleted": task_id, 'tasks': tasks}
    return {'response': "task_id Not found!"}