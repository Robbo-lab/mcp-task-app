from datetime import datetime

from pydantic import BaseModel, Field


# PLTask stands for Pydantic Task
class PLTask(BaseModel):
    model_config = {"from_attributes": True}

    id: int | None = None
    name: str | None = None
    type: str | None = None
    description: str | None = None
    completed: bool | None = False
    task_started: datetime | None = Field(default_factory=datetime.now)
    task_ended: datetime | None = None
