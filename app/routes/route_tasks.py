from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.task_handler import TaskHandler
from app.data.pydantic_objects import PLTask
from app.routes.router_handler import Router
from app.services.database import get_session_api

task_router = Router.task_router


@task_router.get("/get-name", response_model=PLTask, operation_id="get_task_by_name")
def get_task_by_name(
    session: Annotated[Session, Depends(get_session_api)], name: str | None = None
) -> PLTask:
    try:
        if name is None:
            raise HTTPException(status_code=400, detail="name is required")
        task = TaskHandler.get_task(session, name)
    except Exception as e:
        raise e

    if task is None:
        raise HTTPException(
            status_code=404, detail=f"Task with name '{name}' could not be found."
        )

    return task


@task_router.get("/get-id", response_model=PLTask, operation_id="get_task_by_id")
def get_task_by_id(
    session: Annotated[Session, Depends(get_session_api)], task_id: int | None = None
) -> PLTask:
    try:
        if task_id is None:
            raise HTTPException(status_code=400, detail="task_id is required")
        task = TaskHandler.get_task(session, task_id)
    except Exception as e:
        raise e

    if task is None:
        raise HTTPException(
            status_code=404, detail=f"Task with id '{task_id}' could not be found."
        )

    return task


@task_router.post("/delete", operation_id="delete_task_by_name")
def delete_task_by_name(
    session: Annotated[Session, Depends(get_session_api)], name: str | None = None
):
    if name is None:
        raise HTTPException(status_code=400, detail="name is required")
    TaskHandler.delete_task(session, name)


@task_router.post("/add", operation_id="create_task")
def create_task(
    session: Annotated[Session, Depends(get_session_api)], task: PLTask | None = None
) -> PLTask:
    try:
        if task is None:
            raise HTTPException(status_code=400, detail="task is required")
        task = TaskHandler.add_task_to_db(session, task)
    except Exception as e:
        raise e
    return task


@task_router.get("/task-list", operation_id="filter_task_by_type")
def filter_task_by_type(
    session: Annotated[Session, Depends(get_session_api)], task_type: str | None = None
) -> list[PLTask]:
    return TaskHandler.list_tasks(session, task_type)


@task_router.post("/complete", operation_id="complete_task")
def complete_task(
    session: Annotated[Session, Depends(get_session_api)], name: str | None = None
) -> PLTask:
    if name is None:
        raise HTTPException(status_code=400, detail="name is required")
    task = TaskHandler.get_task(session, name)
    return TaskHandler.complete_task(session, task)
