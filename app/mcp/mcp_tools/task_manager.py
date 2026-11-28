"""Define MCP tools for creating, retrieving, updating and deleting tasks.

The tools use TaskHandler for task operations and
DatabaseTaskRepository for database persistence.
"""

from datetime import datetime
from typing import Annotated

from fastapi import Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.api.task_handler import TaskHandler
from app.data.pydantic_objects import PLTask
from app.repositories.database_task_repository import DatabaseTaskRepository
from app.services.database import get_session_api
from app.utils.get_principal import Principal
from app.utils.permissions import (
    enforce_task_read_permissions,
    enforce_task_write_permissions,
)


def get_task_handler(session: Session) -> TaskHandler:
    """Create a task handler using the supplied database session.

    Args:
        session: The database session provided to the MCP tool.

    Returns:
        A TaskHandler configured with a DatabaseTaskRepository.
    """
    repository = DatabaseTaskRepository(session)
    return TaskHandler(repository)


class TaskInput(BaseModel):
    """Input schema for task manager tools."""

    name: str = Field(
        description="Title of the task. Use this when creating or updating a task."
    )
    description: str = Field(
        description="Detailed description of what the task is about."
    )
    completed: bool = Field(
        description="Task completion status. True means completed, False means not completed."
    )
    task_started: datetime = Field(
        description="Date and time when the task was started. Use the current datetime when creating a new task."
    )


class CreateTaskInput(BaseModel):
    """Input schema for creating a new task."""

    task: PLTask = Field(
        description="The task to be created, including its title, description, status, and metadata."
    )


class CompleteTaskInput(BaseModel):
    """Input schema for marking a task as completed."""

    name: str = Field(description="Name of the task to mark as completed.")


class GetTaskByNameInput(BaseModel):
    """Input schema for retrieving a task by its name."""

    name: str = Field(description="Exact name of the task to search for.")


class GetTaskByIdInput(BaseModel):
    """Input schema for retrieving a task by its ID."""

    id: int = Field(description="Exact ID of the task to search for.")


class DeleteTaskByNameInput(BaseModel):
    """Input schema for deleting a task by its name."""

    name: str = Field(description="Exact name of the task to delete.")


class ListTasksInput(BaseModel):
    """Input schema for listing tasks by status."""

    task_type: str = Field(
        description="Task status filter. Valid values are 'Pending' or 'Completed'. Defaults to 'Pending'."
    )


class GetTaskOutput(BaseModel):
    """Response model returned by task manager tools."""

    success: bool = Field(
        description="Indicates whether the operation completed successfully."
    )
    message: str = Field(
        description="Human-readable message describing the result of the operation."
    )
    task: PLTask | None = Field(
        description="The task returned by the operation, or None if no task was found."
    )


class DeleteTaskByNameOutput(BaseModel):
    """Response model for deleting a task."""

    message: str = Field(
        description="Message describing the result of the delete operation."
    )


class CreateTaskOutput(BaseModel):
    """Response model for creating a task."""

    success: bool = Field(
        description="Indicates whether the task was created successfully."
    )
    message: str = Field(
        description="Human-readable message describing the result of the operation."
    )
    task: PLTask | None = Field(
        description="The created task, or None if task creation failed."
    )


class ListTasksOutput(BaseModel):
    """Response model for listing tasks."""

    success: bool = Field(
        description="Indicates whether the tasks were retrieved successfully."
    )
    message: str = Field(
        description="Human-readable message describing the result."
    )
    tasks: list[PLTask] | None = Field(
        description="List of tasks returned by the operation, or None if no tasks were found."
    )


def create_task_tool(
    session: Annotated[Session, Depends(get_session_api)],
    principal: Principal,
    body: CreateTaskInput,
) -> CreateTaskOutput:
    """Create a new task in the task manager.

    Use this tool when the user wants to create or add a new task.
    Do not use it to update, complete, retrieve or delete tasks.

    Args:
        session: Database session used to access task storage.
        principal: Authenticated principal used for permission checks.
        body: Input containing the task details to save.

    Returns:
        CreateTaskOutput indicating whether the task was created
        and containing the created task when successful.
    """
    enforce_task_write_permissions(principal)

    handler = get_task_handler(session)
    task = handler.add_task(body.task)

    if task is None:
        return CreateTaskOutput(
            success=False,
            message=f"Task '{body.task.name}' was not created",
            task=None,
        )

    return CreateTaskOutput(
        success=True,
        message=f"Task '{body.task.name}' was created",
        task=task,
    )


def delete_task_tool(
    session: Annotated[Session, Depends(get_session_api)],
    principal: Principal,
    body: DeleteTaskByNameInput,
) -> DeleteTaskByNameOutput:
    """Delete an existing task using its name.

    Use this tool only when the user explicitly requests that a task
    be deleted or removed.

    Args:
        session: Database session used to access task storage.
        principal: Authenticated principal used for permission checks.
        body: Input containing the exact name of the task to delete.

    Returns:
        DeleteTaskByNameOutput containing the operation result message.
    """
    enforce_task_write_permissions(principal)

    handler = get_task_handler(session)
    handler.delete_task(body.name)

    return DeleteTaskByNameOutput(
        message=f"Task '{body.name}' was deleted",
    )


def get_task_by_name_tool(
    session: Annotated[Session, Depends(get_session_api)],
    principal: Principal,
    body: GetTaskByNameInput,
) -> GetTaskOutput:
    """Retrieve a task using its exact name.

    Use this tool when the user wants to view or find a specific task.

    Args:
        session: Database session used to access task storage.
        principal: Authenticated principal used for permission checks.
        body: Input containing the exact task name.

    Returns:
        GetTaskOutput indicating whether the task was found and
        containing the retrieved task when successful.
    """
    enforce_task_read_permissions(principal)

    handler = get_task_handler(session)
    task = handler.get_task(body.name)

    if task is None:
        return GetTaskOutput(
            success=False,
            message=f"Task '{body.name}' was not found",
            task=None,
        )

    return GetTaskOutput(
        success=True,
        message=f"Task '{body.name}' was retrieved successfully",
        task=task,
    )


def get_task_by_id_tool(
    session: Annotated[Session, Depends(get_session_api)],
    principal: Principal,
    body: GetTaskByIdInput,
) -> GetTaskOutput:
    """Retrieve a task using its unique database ID.

    Use this tool when the user provides the ID of a specific task.

    Args:
        session: Database session used to access task storage.
        principal: Authenticated principal used for permission checks.
        body: Input containing the integer task ID.

    Returns:
        GetTaskOutput indicating whether the task was found and
        containing the retrieved task when successful.
    """
    enforce_task_read_permissions(principal)

    handler = get_task_handler(session)
    task = handler.get_task(body.id)

    if task is None:
        return GetTaskOutput(
            success=False,
            message=f"Task '{body.id}' was not found",
            task=None,
        )

    return GetTaskOutput(
        success=True,
        message=f"Task '{body.id}' was retrieved successfully",
        task=task,
    )


def list_tasks_tool(
    session: Annotated[Session, Depends(get_session_api)],
    principal: Principal,
    body: ListTasksInput,
) -> ListTasksOutput:
    """Retrieve tasks filtered by task type.

    Use this tool when the user wants to view multiple tasks,
    such as tasks belonging to a particular type.

    Args:
        session: Database session used to access task storage.
        principal: Authenticated principal used for permission checks.
        body: Input containing the task type filter.

    Returns:
        ListTasksOutput containing the matching tasks and the
        result of the retrieval operation.
    """
    enforce_task_read_permissions(principal)

    handler = get_task_handler(session)
    filtered_tasks = handler.list_tasks(body.task_type)

    if not filtered_tasks:
        return ListTasksOutput(
            success=False,
            message="No matching tasks were found",
            tasks=[],
        )

    return ListTasksOutput(
        success=True,
        message="Tasks retrieved successfully",
        tasks=filtered_tasks,
    )


def complete_task_tool(
    session: Annotated[Session, Depends(get_session_api)],
    principal: Principal,
    body: CompleteTaskInput,
) -> GetTaskOutput:
    """Mark an existing task as completed.

    Use this tool when the user wants to finish or mark a task as done.

    Args:
        session: Database session used to access task storage.
        principal: Authenticated principal used for permission checks.
        body: Input containing the name of the task to complete.

    Returns:
        GetTaskOutput indicating whether the task was completed and
        containing the updated task when successful.
    """
    enforce_task_write_permissions(principal)

    handler = get_task_handler(session)
    task = handler.get_task(body.name)

    if task is None:
        return GetTaskOutput(
            success=False,
            message=f"Task '{body.name}' was not found",
            task=None,
        )

    completed_task = handler.complete_task(task)

    return GetTaskOutput(
        success=True,
        message=f"Task '{body.name}' was completed",
        task=completed_task,
    )


TOOL_DEFINITION = [
    {
        "name": "create_task",
        "description": (
            "Create a new task in the task manager. "
            "Use when the user wants to add a task."
        ),
        "func": create_task_tool,
        "tags": {"task", "create", "add"},
    },
    {
        "name": "delete_task",
        "description": (
            "Delete an existing task by its name. "
            "Use only when the user explicitly requests task removal."
        ),
        "func": delete_task_tool,
        "tags": {"task", "delete", "remove"},
    },
    {
        "name": "get_task_by_name",
        "description": (
            "Retrieve a task using its exact name. "
            "Use when the user wants to view information about a specific task."
        ),
        "func": get_task_by_name_tool,
        "tags": {"task", "get", "find", "search", "name"},
    },
    {
        "name": "get_task_by_id",
        "description": (
            "Retrieve a task using its unique identifier. "
            "Use when the task ID is known."
        ),
        "func": get_task_by_id_tool,
        "tags": {"task", "get", "find", "search", "id"},
    },
    {
        "name": "list_tasks",
        "description": (
            "List tasks filtered by status. Use to retrieve pending or completed tasks."
        ),
        "func": list_tasks_tool,
        "tags": {"task", "list", "filter", "completed", "pending"},
    },
    {
        "name": "complete_task",
        "description": (
            "Mark a task as completed. "
            "Use when the user wants to finish, complete, or mark a task as done."
        ),
        "func": complete_task_tool,
        "tags": {"task", "complete", "finish", "done"},
    },
]
