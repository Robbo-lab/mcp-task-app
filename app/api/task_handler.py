from datetime import datetime

from fastapi import HTTPException

from app.data.pydantic_objects import PLTask
from app.repositories.task_repository import TaskRepository


class TaskHandler:
    """Handles task operations using a task repository."""

    def __init__(self, repository: TaskRepository):
        self.repository = repository

    @staticmethod
    def create_task(
        name: str,
        _type: str,
        description: str,
        completed: bool = False,
    ) -> PLTask:
        return PLTask(
            name=name,
            type=_type,
            description=description,
            completed=completed,
        )

    def add_task(self, task: PLTask) -> PLTask:
        """Create and save a task."""
        return self.repository.add(task)

    def delete_task(self, name_or_id: int | str) -> None:
        """Delete a task by name or ID."""
        if not isinstance(name_or_id, (int, str)):
            raise TypeError("name_or_id must be either a name or an ID")

        self.repository.delete(name_or_id)

    def get_task(self, name_or_id: str | int) -> PLTask | None:
        """Retrieve a task by name or ID."""
        if isinstance(name_or_id, str):
            return self.repository.get_by_name(name_or_id)

        if isinstance(name_or_id, int):
            return self.repository.get_by_id(name_or_id)

        raise TypeError("name_or_id must be either a name or an ID")

    def list_tasks(
        self,
        task_type: str | None = None,
    ) -> list[PLTask]:
        """Retrieve tasks, optionally filtered by type."""
        return self.repository.list(task_type)

    def complete_task(self, task: PLTask) -> PLTask:
        """Mark a task as completed."""
        if task.id is None:
            raise HTTPException(
                status_code=400,
                detail="task id is required",
            )

        task.completed = True
        task.task_ended = datetime.now()

        try:
            updated_task = self.repository.update(task)
        except Exception as err:
            raise HTTPException(
                status_code=500,
                detail=str(err),
            ) from err

        if updated_task is None:
            raise HTTPException(
                status_code=404,
                detail="Task not found",
            )

        return updated_task

    @staticmethod
    def task_run_duration(task: PLTask) -> float:
        """Return the duration of a completed task."""
        if task.task_started and task.task_ended:
            time_elapsed = task.task_ended - task.task_started
            return time_elapsed.total_seconds()

        raise HTTPException(
            status_code=500,
            detail="Task hasn't finished running",
        )