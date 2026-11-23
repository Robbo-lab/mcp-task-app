from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.task_handler import TaskHandler
from app.data.pydantic_objects import PLTask
from app.routes.router_handler import Router
from app.services.database import get_session_api

task_router = Router.task_router


# Search for a task by name
@task_router.get("/tasks/by-name/{name}", response_model=PLTask)
def get_task_by_name(
    session: Annotated[Session, Depends(get_session_api)], name: str
) -> PLTask:
    """Retrieve a task by its name or return 404 if not found."""
    task = TaskHandler.get_task(session, name)

    if not task:
        raise HTTPException(
            status_code=404, detail=f"Task with name '{name}' could not be found."
        )

    return task


# Search for a task by ID
@task_router.get("/tasks/{task_id}", response_model=PLTask)
def get_task_by_id(
    session: Annotated[Session, Depends(get_session_api)], task_id: int
) -> PLTask:
    """Retrieve a task by its ID or return 404 if not found."""
    task = TaskHandler.get_task(session, task_id)

    if not task:
        raise HTTPException(
            status_code=404, detail=f"Task with id '{task_id}' could not be found."
        )
    return task


# Delete a task by name
@task_router.delete("/tasks/by-name/{name}")
def delete_task_by_name(
    session: Annotated[Session, Depends(get_session_api)], name: str
):
    """Delete a task by its name."""
    TaskHandler.delete_task(session, name)


# Create a task in a Schema
@task_router.post("/tasks")
def create_task(
    session: Annotated[Session, Depends(get_session_api)], task: PLTask
) -> PLTask:
    """Create and save a new task in the database."""
    return TaskHandler.add_task_to_db(session, task)


# List all the tasks, with or without parameters
@task_router.get("/tasks")
def filter_task_by_type(
    session: Annotated[Session, Depends(get_session_api)], task_type: str | None = None
) -> list[PLTask]:
    """List all tasks or filter them by type."""
    return TaskHandler.list_tasks(session, task_type)


# Complete a task by name
@task_router.patch("/tasks/by-name/{name}/complete")
def complete_task(
    session: Annotated[Session, Depends(get_session_api)], name: str
) -> PLTask:
    """Mark a task as completed using its name."""
    task = TaskHandler.get_task(session, name)
    return TaskHandler.complete_task(session, task)
