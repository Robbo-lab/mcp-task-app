
from datetime import datetime

from fastapi import HTTPException

from app.data.pydantic_objects import PLTask
from app.repositories.task_repository import TaskRepository


class TaskHandler:
    """Handles task operations using a task repository."""

    def __init__(self, repository: TaskRepository) -> None:
        """Initialise the TaskHandler with a task repository.

        Args:
            repository: The repository used to access task storage.
        """
        self.repository: TaskRepository = repository

    @staticmethod
    def create_task(
        name: str,
        _type: str,
        description: str,
        completed: bool = False,
    ) -> PLTask:
        """Create a new task object.

        Args:
            name: The name of the task.
            _type: The type or category of the task.
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
        """Add a task to the repository.

        Args:
            task: The task to save.

        Returns:
            The saved task.
        """
        return self.repository.add(task)

    def delete_task(self, name_or_id: int | str) -> None:
        """Delete a task using its name or ID.

        Args:
            name_or_id: The name or ID of the task to delete.

        Raises:
            TypeError: If the identifier is not a string or integer.
        """
        if not isinstance(name_or_id, (int, str)):
            raise TypeError("name_or_id must be either a name or an ID")

        self.repository.delete(name_or_id)

    def get_task(self, name_or_id: str | int) -> PLTask | None:
        """Retrieve a task using its name or ID.

        Args:
            name_or_id: The name or ID of the task to retrieve.

        Raises:
            TypeError: If the identifier is not a string or integer.

        Returns:
            The matching task, or None if no task is found.
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
        """Retrieve tasks, optionally filtered by type.

        Args:
            task_type: The task type used to filter the results.

        Returns:
            A list of matching tasks.
        """
        return self.repository.list(task_type)

    def complete_task(self, task: PLTask) -> PLTask:
        """Mark a task as completed and save the changes.

        Args:
            task: The task to mark as completed.

        Raises:
            HTTPException: If the task has no ID, an update fails,
                or the task cannot be found.

        Returns:
            The updated completed task.
        """
        if task.id is None:
            raise HTTPException(
                status_code=400,
                detail="task id is required",
            )

        task.completed = True
        task.task_ended = datetime.now()

        try:
            updated_task: PLTask | None = self.repository.update(task)
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
        """Calculate the duration of a completed task.

        Args:
            task: The task containing its start and end timestamps.

        Raises:
            HTTPException: If the task has not finished running.

        Returns:
            The elapsed task duration in seconds.
        """
        if task.task_started and task.task_ended:
            time_elapsed = task.task_ended - task.task_started
            return time_elapsed.total_seconds()

        raise HTTPException(
            status_code=500,
            detail="Task hasn't finished running",
        )
