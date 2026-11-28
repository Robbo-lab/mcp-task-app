
"""Handle task operations independently of the storage implementation."""

from datetime import datetime

from fastapi import HTTPException

from app.data.pydantic_objects import PLTask
from app.repositories.task_repository import TaskRepository


class TaskHandler:
    """Handle task operations using an injected repository.

    The handler contains task-related application logic and delegates
    storage operations to the supplied TaskRepository implementation.

    Attributes:
        repository: The repository used to access task storage.
    """

    def __init__(self, repository: TaskRepository):
        """Initialise the handler with a task repository.

        Args:
            repository: The repository used for task storage operations.
        """
        self.repository = repository

    @staticmethod
    def create_task(
        name: str,
        _type: str,
        description: str,
        completed: bool = False,
    ) -> PLTask:
        """Create a PLTask object without saving it.

        Args:
            name: The name of the task.
            _type: The type assigned to the task.
            description: A description of the task.
            completed: Whether the task has been completed.

        Returns:
            A new PLTask instance.
        """
        return PLTask(
            name=name,
            type=_type,
            description=description,
            completed=completed,
        )

    def add_task(self, task: PLTask) -> PLTask:
        """Save a task using the configured repository.

        Args:
            task: The task to save.

        Returns:
            The saved task, including its generated ID.
        """
        return self.repository.add(task)

    def delete_task(self, name_or_id: int | str) -> None:
        """Delete a task using its name or ID.

        Args:
            name_or_id: The name or integer ID of the task to delete.

        Raises:
            TypeError: If the supplied identifier is not a string or integer.
        """
        if not isinstance(name_or_id, (int, str)):
            raise TypeError("name_or_id must be either a name or an ID")

        self.repository.delete(name_or_id)

    def get_task(self, name_or_id: str | int) -> PLTask | None:
        """Retrieve a task using its name or ID.

        Args:
            name_or_id: The exact task name or integer database ID.

        Returns:
            The matching task, or None if it cannot be found.

        Raises:
            TypeError: If the supplied identifier is not a string or integer.
        """
        if isinstance(name_or_id, str):
            return self.repository.get_by_name(name_or_id)

        if isinstance(name_or_id, int):
            return self.repository.get_by_id(name_or_id)

        raise TypeError("name_or_id must be either a name or an ID")

    def list_tasks(
        self,
        task_type: str | None = None,
    ) -> list[PLTask]:
        """Retrieve tasks, optionally filtering by type.

        Args:
            task_type: The task type to filter by. If None, all tasks
                are returned.

        Returns:
            A list of matching tasks. An empty list is returned when
            no tasks match the requested filter.
        """
        return self.repository.list(task_type)

    def complete_task(self, task: PLTask) -> PLTask:
        """Mark an existing task as completed.

        Sets the task's completion status and end time, then asks
        the repository to persist the changes.

        Args:
            task: The task to mark as completed. It must have a database ID.

        Returns:
            The updated task.

        Raises:
            HTTPException: If the task has no ID, cannot be found,
                or an error occurs while updating it.
        """
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
        """Calculate the elapsed time for a completed task.

        Args:
            task: The task containing its start and end timestamps.

        Returns:
            The elapsed time in seconds.

        Raises:
            HTTPException: If the task has not finished or is missing
                either timestamp.
        """
        if task.task_started and task.task_ended:
            time_elapsed = task.task_ended - task.task_started
            return time_elapsed.total_seconds()

        raise HTTPException(
            status_code=500,
            detail="Task hasn't finished running",
        )
