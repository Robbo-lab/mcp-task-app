
from datetime import datetime

from sqlalchemy.orm import Session

from app.data.database_objects import DBTask
from app.data.pydantic_objects import PLTask
from app.repositories.task_repository import TaskRepository
from app.services.database import DataBaseMethods


class DatabaseTaskRepository(TaskRepository):
    """Implement task storage operations using the database."""

    def __init__(self, db: Session) -> None:
        """Initialise the repository with a database session.

        Args:
            db: The SQLAlchemy database session.
        """
        self.db: Session = db

    def add(self, task: PLTask) -> PLTask:
        """Add a task to the database.

        Args:
            task: The task to add to the database.

        Raises:
            Exception: If the task could not be created.

        Returns:
            The saved task with its database ID.
        """
        new_task: DBTask = DBTask(
            id=task.id or None,
            name=task.name,
            type=task.type,
            description=task.description,
            completed=task.completed or False,
            task_started=task.task_started or datetime.now(),
        )

        new_task = DataBaseMethods.add_object(self.db, new_task)

        if new_task is None:
            raise Exception("No new task object was created")

        task.id = new_task.id
        return task

    def get_by_id(self, task_id: int) -> PLTask | None:
        """Retrieve a task from the database using its ID.

        Args:
            task_id: The ID of the task to retrieve.

        Returns:
            The matching task, or None if not found.
        """
        db_task: DBTask | None = DataBaseMethods.get_object_by_id(
            self.db, DBTask, task_id
        )

        if db_task is None:
            return None

        return PLTask.model_validate(db_task)

    def get_by_name(self, name: str) -> PLTask | None:
        """Retrieve a task from the database using its name.

        Args:
            name: The name of the task to retrieve.

        Returns:
            The matching task, or None if not found.
        """
        db_task: DBTask | None = DataBaseMethods.get_object_by_name(
            self.db, DBTask, name
        )

        if db_task is None:
            return None

        return PLTask.model_validate(db_task)

    def list(self, task_type: str | None = None) -> list[PLTask]:
        """Retrieve tasks from the database, optionally filtered by type.

        Args:
            task_type: The task type used to filter the results.
                If None, all tasks are returned.

        Returns:
            A list of matching tasks.
        """
        query = self.db.query(DBTask)

        if task_type is not None:
            query = query.filter(DBTask.type == task_type)

        db_tasks: list[DBTask] = query.all()

        return [
            PLTask.model_validate(db_task)
            for db_task in db_tasks
        ]

    def delete(self, name_or_id: str | int) -> None:
        """Delete a task using its name or ID.

        Args:
            name_or_id: The name or ID of the task to delete.

        Raises:
            TypeError: If the identifier is not a string or integer.
        """
        if isinstance(name_or_id, int):
            db_task: DBTask | None = DataBaseMethods.get_object_by_id(
                self.db, DBTask, name_or_id
            )
        elif isinstance(name_or_id, str):
            db_task = DataBaseMethods.get_object_by_name(
                self.db, DBTask, name_or_id
            )
        else:
            raise TypeError("name_or_id must be either a name or an ID")

        if db_task is not None:
            DataBaseMethods.delete_object(self.db, db_task)

    def update(self, task: PLTask) -> PLTask | None:
        """Update an existing task in the database.

        Args:
            task: The task containing the updated information.

        Returns:
            The updated task, or None if the task ID is missing
            or the task cannot be found.
        """
        if task.id is None:
            return None

        db_task: DBTask | None = (
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
