
from abc import ABC, abstractmethod

from app.data.pydantic_objects import PLTask


class TaskRepository(ABC):
    """Define the interface for accessing task storage."""

    @abstractmethod
    def add(self, task: PLTask) -> PLTask:
        """Add a task to storage.

        Args:
            task: The task to add.

        Returns:
            The newly saved task.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, task_id: int) -> PLTask | None:
        """Retrieve a task using its ID.

        Args:
            task_id: The ID of the task to retrieve.

        Returns:
            The matching task, or None if not found.
        """
        raise NotImplementedError

    @abstractmethod
    def get_by_name(self, name: str) -> PLTask | None:
        """Retrieve a task using its name.

        Args:
            name: The name of the task to retrieve.

        Returns:
            The matching task, or None if not found.
        """
        raise NotImplementedError

    @abstractmethod
    def delete(self, name_or_id: str | int) -> None:
        """Delete a task using its name or ID.

        Args:
            name_or_id: The name or ID of the task to delete.

        Returns:
            None.
        """
        raise NotImplementedError

    @abstractmethod
    def list(self, task_type: str | None = None) -> list[PLTask]:
        """Retrieve tasks, optionally filtered by type.

        Args:
            task_type: The task type used to filter the results.
                If None, all tasks are returned.

        Returns:
            A list of matching tasks.
        """
        raise NotImplementedError

    @abstractmethod
    def update(self, task: PLTask) -> PLTask | None:
        """Update an existing task in storage.

        Args:
            task: The task containing the updated information.

        Returns:
            The updated task, or None if the task was not found.
        """
        raise NotImplementedError
