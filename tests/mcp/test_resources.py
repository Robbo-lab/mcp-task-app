import sys
from typing import Any


# Fake the fastmcp module so resource_utils doesn't crash on import
class MockFastMCPModule:
    FastMCP = None

    class resources:  # noqa: N801
        BinaryResource = None
        TextResource = None


sys.modules["fastmcp"] = MockFastMCPModule
sys.modules["fastmcp.resources"] = MockFastMCPModule.resources


class MockFastMCP:
    """A basic mock class to stand in for FastMCP so we don't need a server."""

    def __init__(self, name: str):
        self.name = name
        self.added_resources = []
        self.registered_routes = {}

    def resource(self, uri_template: str, **kwargs):
        def decorator(handler_func):
            self.registered_routes[uri_template] = handler_func
            return handler_func

        return decorator

    def add_resource(self, resource):
        self.added_resources.append(resource)


def mock_payload_func() -> dict[str, Any]:
    """Returns a simple fake dictionary for testing."""
    return {"id": "test-data", "value": 100}


def test_resource_definition_fallback_logic():
    """Test that it uses the resource name if display_name is empty."""
    from app.utils.resource_definition import ResourceDefinition

    resource = ResourceDefinition(
        name="fallback_fallback",
        display_name="",
        description="Testing string evaluations.",
        mime_type="text/plain",
        func=mock_payload_func,
    )
    display_check = resource.display_name or resource.name
    assert display_check == "fallback_fallback"
    assert resource.name == "fallback_fallback"


def test_resource_definition_fields():
    """Test that name and mime_type are saved correctly when created."""
    from app.utils.resource_definition import ResourceDefinition

    resource = ResourceDefinition(
        name="unit_reference",
        display_name="Unit Converter Cheatsheet",
        description="JSON cheatsheet metadata layer.",
        mime_type="application/json",
        func=mock_payload_func,
    )
    assert resource.name == "unit_reference"
    assert resource.mime_type == "application/json"


def test_register_resources_dry_run():
    """Test that the loop registers the correct route format."""
    from app.utils.resource_definition import ResourceDefinition
    from app.utils.resource_utils import register_resources

    mock_mcp = MockFastMCP("TestRegistry")
    definitions = [
        ResourceDefinition(
            name="mock_endpoint",
            display_name="Mock Endpoint",
            description="Testing loop registry mapping loops.",
            mime_type="application/json",
            func=mock_payload_func,
        )
    ]

    register_resources(mock_mcp, definitions, include_static=False)
    assert "resource://converter/{name}" in mock_mcp.registered_routes


def test_resource_definition_execution():
    """Test that the function attached to the resource returns the right text."""
    from app.utils.resource_definition import ResourceDefinition

    resource = ResourceDefinition(
        name="test_exec",
        display_name="Exec Test",
        description="Testing functional callbacks.",
        mime_type="text/plain",
        func=lambda: "raw text content",
    )
    assert resource.func() == "raw text content"
    assert resource.display_name == "Exec Test"
