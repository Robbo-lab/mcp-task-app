from abc import ABC, abstractmethod

from app.data.pydantic_objects import PLTask


class TaskRepository(ABC):
    """Defines the methods used to access task storage."""

    @abstractmethod
    def add(self, task: PLTask) -> PLTask:
        """Add a task to storage."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, task_id: int) -> PLTask | None:
        """Retrieve a task using its ID."""
        raise NotImplementedError

    @abstractmethod
    def get_by_name(self, name: str) -> PLTask | None:
        """Retrieve a task using its name."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, name_or_id: str | int) -> None:
        """Delete a task using its name or ID."""
        raise NotImplementedError

    @abstractmethod
    def list(self, task_type: str | None = None) -> list[PLTask]:
        """Get tasks, optionally filtered by type."""
        raise NotImplementedError

    @abstractmethod
    def update(self, task: PLTask) -> PLTask | None:
        """Update an existing task."""
        raise NotImplementedError