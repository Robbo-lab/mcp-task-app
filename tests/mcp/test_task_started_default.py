import time

from app.data.pydantic_objects import PLTask


def test_task_started_is_created_per_instance():
    first = PLTask(name="first")
    time.sleep(0.001)
    second = PLTask(name="second")

    assert first.task_started is not None
    assert second.task_started is not None
    assert first.task_started < second.task_started


def test_task_started_schema_has_no_frozen_default():
    schema = PLTask.model_json_schema()

    assert "default" not in schema["properties"]["task_started"]
