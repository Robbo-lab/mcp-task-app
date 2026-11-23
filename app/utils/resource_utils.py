import json
from collections.abc import Iterable
from typing import Any

from fastmcp import FastMCP
from fastmcp.resources import BinaryResource, TextResource
from pydantic import AnyUrl

from app.utils.resource_definition import ResourceDefinition


def register_resources(  # noqa: C901
    mcp: FastMCP,
    definitions: Iterable[ResourceDefinition],
    uri_template: str = "resource://converter/{name}",
    include_static: bool = True,
) -> None:
    """Loops through the resource list and registers them on the MCP server.

    Args:
        mcp: The main FastMCP server app.
        definitions: The list of resource setups to loop through.
        uri_template: The URL pattern used to create paths.
        include_static: Set to True to add individual fixed URIs.
    """
    lookup_table: dict[str, ResourceDefinition] = {}

    for define in definitions:
        lookup_table[define.name] = define

    def as_text(value: Any) -> str:
        if isinstance(value, str):
            return value
        if isinstance(value, dict):
            return json.dumps(value, indent=2)
        return str(value)

    def handler(name: str) -> str:
        if name not in lookup_table:
            raise ValueError(f"Unknown resource name '{name}'")
        definition = lookup_table[name]
        content = definition.func()
        if not isinstance(content, (bytes, bytearray)):
            return as_text(content)
        return content

    # Dynamic template (with parameters)
    mcp.resource(
        uri_template,
        name="Converter resources",
        description="Dynamic converter resources",
        mime_type="text/plain",
    )(handler)

    # Concrete URIs for discoverability in inspectors
    if include_static:
        for definition in definitions:
            uri = uri_template.replace("{name}", definition.name)
            mime = definition.mime_type
            content = definition.func()
            payload = (
                content if isinstance(content, (bytes, bytearray)) else as_text(content)
            )
            if isinstance(payload, (bytes, bytearray)):
                resource = BinaryResource(
                    uri=AnyUrl(uri),
                    name=definition.display_name or definition.name,
                    mime_type=mime,
                    data=bytes(payload),
                )
            else:
                resource = TextResource(
                    uri=AnyUrl(uri),
                    name=definition.display_name or definition.name,
                    mime_type=mime,
                    text=payload,
                )
            mcp.add_resource(resource)
