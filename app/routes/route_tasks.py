
"""Define API routes for task management."""

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
    """Create a task handler using the supplied database session.

    Args:
        session: The database session provided by the API dependency.

    Returns:
        A TaskHandler configured with a DatabaseTaskRepository.
    """
    repository = DatabaseTaskRepository(session)
    return TaskHandler(repository)


@task_router.get("/get-name", response_model=PLTask)
def get_task_by_name(
    session: Annotated[Session, Depends(get_session_api)],
    name: str | None = None,
) -> PLTask:
    """Retrieve a task using its name.

    Args:
        session: The database session for the current request.
        name: The exact name of the task to retrieve.

    Returns:
        The matching task.

    Raises:
        HTTPException: If the name is missing or the task cannot be found.
    """
    if name is None:
        raise HTTPException(status_code=400, detail="name is required")

    task = get_task_handler(session).get_task(name)

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
    """Retrieve a task using its database ID.

    Args:
        session: The database session for the current request.
        task_id: The integer ID of the task to retrieve.

    Returns:
        The matching task.

    Raises:
        HTTPException: If the ID is missing or the task cannot be found.
    """
    if task_id is None:
        raise HTTPException(status_code=400, detail="task_id is required")

    task = get_task_handler(session).get_task(task_id)

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
):
    """Delete a task using its name.

    Args:
        session: The database session for the current request.
        name: The exact name of the task to delete.

    Raises:
        HTTPException: If the task name is missing.
    """
    if name is None:
        raise HTTPException(status_code=400, detail="name is required")

    get_task_handler(session).delete_task(name)


@task_router.post("/add")
def create_task(
    session: Annotated[Session, Depends(get_session_api)],
    task: PLTask | None = None,
) -> PLTask:
    """Create and save a new task.

    Args:
        session: The database session for the current request.
        task: The task details to save.

    Returns:
        The saved task, including its database ID.

    Raises:
        HTTPException: If the task is not supplied.
    """
    if task is None:
        raise HTTPException(status_code=400, detail="task is required")

    return get_task_handler(session).add_task(task)


@task_router.get("/task-list")
def filter_task_by_type(
    session: Annotated[Session, Depends(get_session_api)],
    task_type: str | None = None,
) -> list[PLTask]:
    """Retrieve tasks, optionally filtering by task type.

    Args:
        session: The database session for the current request.
        task_type: Optional task type used to filter the results.

    Returns:
        A list of matching tasks. An empty list is returned if there
        are no matching tasks.
    """
    return get_task_handler(session).list_tasks(task_type)


@task_router.post("/complete")
def complete_task(
    session: Annotated[Session, Depends(get_session_api)],
    name: str | None = None,
) -> PLTask:
    """Mark a task as completed using its name.

    Args:
        session: The database session for the current request.
        name: The exact name of the task to complete.

    Returns:
        The updated task.

    Raises:
        HTTPException: If the name is missing or the task cannot be found.
    """
    if name is None:
        raise HTTPException(status_code=400, detail="name is required")

    handler = get_task_handler(session)
    task = handler.get_task(name)

    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")

    return handler.complete_task(task)
