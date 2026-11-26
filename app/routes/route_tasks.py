
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.task_handler import TaskHandler
from app.data.pydantic_objects import PLTask
from app.repositories.database_task_repository import DatabaseTaskRepository
from app.routes.router_handler import Router
from app.services.database import get_session_api

task_router = Router.task_router


def get_task_handler(session: Session) -> TaskHandler:
    """Create a TaskHandler with a database repository.

    Args:
        session: The SQLAlchemy database session.

    Returns:
        A TaskHandler instance using the database repository.
    """
    repository: DatabaseTaskRepository = DatabaseTaskRepository(session)
    return TaskHandler(repository)


@task_router.get("/get-name", response_model=PLTask)
def get_task_by_name(
    session: Annotated[Session, Depends(get_session_api)],
    name: str | None = None,
) -> PLTask:
    """Retrieve a task using its name.

    Args:
        session: The SQLAlchemy database session.
        name: The name of the task to retrieve.

    Raises:
        HTTPException: If the name is missing or the task is not found.

    Returns:
        The requested task.
    """
    if name is None:
        raise HTTPException(status_code=400, detail="name is required")

    task: PLTask | None = get_task_handler(session).get_task(name)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with name '{name}' could not be found.",
        )

    return task


@task_router.get("/get-id", response_model=PLTask)
def get_task_by_id(
    session: Annotated[Session, Depends(get_session_api)],
    task_id: int | None = None,
) -> PLTask:
    """Retrieve a task using its ID.

    Args:
        session: The SQLAlchemy database session.
        task_id: The ID of the task to retrieve.

    Raises:
        HTTPException: If the task ID is missing or the task is not found.

    Returns:
        The requested task.
    """
    if task_id is None:
        raise HTTPException(status_code=400, detail="task_id is required")

    task: PLTask | None = get_task_handler(session).get_task(task_id)

    if task is None:
        raise HTTPException(
            status_code=404,
            detail=f"Task with id '{task_id}' could not be found.",
        )

    return task


@task_router.post("/delete")
def delete_task_by_name(
    session: Annotated[Session, Depends(get_session_api)],
    name: str | None = None,
) -> None:
    """Delete a task using its name.

    Args:
        session: The SQLAlchemy database session.
        name: The name of the task to delete.

    Raises:
        HTTPException: If the task name is missing.
    """
    if name is None:
        raise HTTPException(status_code=400, detail="name is required")

    get_task_handler(session).delete_task(name)


@task_router.post("/add", response_model=PLTask)
def create_task(
    session: Annotated[Session, Depends(get_session_api)],
    task: PLTask | None = None,
) -> PLTask:
    """Create a new task.

    Args:
        session: The SQLAlchemy database session.
        task: The task details to add.

    Raises:
        HTTPException: If the task details are missing.

    Returns:
        The newly created task.
    """
    if task is None:
        raise HTTPException(status_code=400, detail="task is required")

    return get_task_handler(session).add_task(task)


@task_router.get("/task-list", response_model=list[PLTask])
def filter_task_by_type(
    session: Annotated[Session, Depends(get_session_api)],
    task_type: str | None = None,
) -> list[PLTask]:
    """Retrieve tasks, optionally filtered by type.

    Args:
        session: The SQLAlchemy database session.
        task_type: The task type used to filter the results.

    Returns:
        A list of tasks matching the specified type.
    """
    return get_task_handler(session).list_tasks(task_type)


@task_router.post("/complete", response_model=PLTask)
def complete_task(
    session: Annotated[Session, Depends(get_session_api)],
    name: str | None = None,
) -> PLTask:
    """Mark a task as complete using its name.

    Args:
        session: The SQLAlchemy database session.
        name: The name of the task to complete.

    Raises:
        HTTPException: If the task name is missing or the task is not found.

    Returns:
        The completed task.
    """
    if name is None:
        raise HTTPException(status_code=400, detail="name is required")

    handler: TaskHandler = get_task_handler(session)
    task: PLTask | None = handler.get_task(name)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return handler.complete_task(task)
