from sqlalchemy.orm import Session
from app.data.pydantic_objects import PLTask
from app.repositories.task_repository import TaskRepository


class DatabaseTaskRepository(TaskRepository):
    """Implements task storage operations using the database."""
    def __init__(self, db: Session):
        self.db = db

    def add(self, task: PLTask) -> PLTask:
        """Add a task to the database."""
        raise NotImplementedError
    
    def get_by_id(self, task_id: int) -> PLTask | None:
        """Find a task using its ID."""
        raise NotImplementedError
    
    def get_by_name(self, name: str) -> PLTask | None:
        """Find a task using its name."""
        raise NotImplementedError
    
    def list_tasks(self, task_type: str | None = None) -> list[PLTask]:
        """Get tasks, optionally filtered by type."""
        raise NotImplementedError
    
    def delete(self, name_or_id: str | int) -> None:
        """Delete a task using its name or ID."""
        raise NotImplementedError
    
    def update(self, task: PLTask) -> PLTask:
        """Update an existing task in the database."""
        raise NotImplementedError
    