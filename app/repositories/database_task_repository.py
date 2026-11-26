
"""Provide SQLAlchemy-based storage operations for tasks."""

from datetime import datetime

from sqlalchemy.orm import Session

from app.data.database_objects import DBTask
from app.data.pydantic_objects import PLTask
from app.repositories.task_repository import TaskRepository
from app.services.database import DataBaseMethods


class DatabaseTaskRepository(TaskRepository):
    """Implement task storage operations using SQLAlchemy.

    This repository converts between the application's PLTask model
    and the database DBTask model.

    Attributes:
        db: The SQLAlchemy session used for database operations.
    """

    def __init__(self, db: Session):
        """Initialise the repository with an existing database session.

        Args:
            db: The SQLAlchemy session supplied by the application.
        """
        self.db = db

    def add(self, task: PLTask) -> PLTask:
        """Save a task to the database.

        Converts the supplied PLTask into a DBTask, persists it,
        and copies the generated database ID back to the original task.

        Args:
            task: The task to save.

        Returns:
            The task with its database-generated ID.

        Raises:
            HTTPException: If the database operation fails.
        """
        new_task = DBTask(
            id=task.id or None,
            name=task.name,
            type=task.type,
            description=task.description,
            completed=task.completed or False,
            task_started=task.task_started or datetime.now(),
        )

        new_task = DataBaseMethods.add_object(self.db, new_task)

        if new_task is None:
            raise RuntimeError("No new task object was created")

        task.id = new_task.id
        return task

    def get_by_id(self, task_id: int) -> PLTask | None:
        """Retrieve a task from the database by its ID.

        Args:
            task_id: The database ID of the task.

        Returns:
            The matching task as a PLTask, or None if it does not exist.
        """
        db_task = DataBaseMethods.get_object_by_id(
            self.db,
            DBTask,
            task_id,
        )

        if db_task is None:
            return None

        return PLTask.model_validate(db_task)

    def get_by_name(self, name: str) -> PLTask | None:
        """Retrieve a task from the database by its name.

        Args:
            name: The exact name of the task.

        Returns:
            The matching task as a PLTask, or None if it does not exist.
        """
        db_task = DataBaseMethods.get_object_by_name(
            self.db,
            DBTask,
            name,
        )

        if db_task is None:
            return None

        return PLTask.model_validate(db_task)

    def list(self, task_type: str | None = None) -> list[PLTask]:
        """Retrieve tasks from the database.

        Args:
            task_type: Optional task type used to filter the results.
                If None, all tasks are returned.

        Returns:
            A list of matching tasks. Returns an empty list if no
            tasks match the requested filter.
        """
        query = self.db.query(DBTask)

        if task_type is not None:
            query = query.filter(DBTask.type == task_type)

        db_tasks = query.all()

        return [
            PLTask.model_validate(db_task)
            for db_task in db_tasks
        ]

    def delete(self, name_or_id: str | int) -> None:
        """Delete a task from the database by name or ID.

        Args:
            name_or_id: The exact task name or integer database ID.

        Raises:
            TypeError: If the supplied identifier is not a string or integer.
        """
        if isinstance(name_or_id, int):
            db_task = DataBaseMethods.get_object_by_id(
                self.db,
                DBTask,
                name_or_id,
            )
        elif isinstance(name_or_id, str):
            db_task = DataBaseMethods.get_object_by_name(
                self.db,
                DBTask,
                name_or_id,
            )
        else:
            raise TypeError("name_or_id must be either a name or an ID")

        if db_task is not None:
            DataBaseMethods.delete_object(self.db, db_task)

    def update(self, task: PLTask) -> PLTask | None:
        """Update an existing task in the database.

        The task ID is used to locate the database record. All task
        fields managed by this repository are then updated.

        Args:
            task: The task containing the updated values.

        Returns:
            The updated task, or None if it has no ID or cannot be found.

        Raises:
            Exception: Re-raises database errors after rolling back
                the current transaction.
        """
        if task.id is None:
            return None

        db_task = (
            self.db.query(DBTask)
            .filter(DBTask.id == task.id)
            .first()
        )

        if db_task is None:
            return None

        db_task.name = task.name
        db_task.type = task.type
        db_task.description = task.description
        db_task.completed = task.completed
        db_task.task_started = task.task_started
        db_task.task_ended = task.task_ended

        try:
            self.db.commit()
            self.db.refresh(db_task)
        except Exception:
            self.db.rollback()
            raise

        return PLTask.model_validate(db_task)
