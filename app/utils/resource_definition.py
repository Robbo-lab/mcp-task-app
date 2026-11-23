from collections.abc import Callable
from dataclasses import dataclass
from typing import Any


@dataclass
class ResourceDefinition:
    """A simple dataclass to hold all the setup data for an MCP resource.

    Attributes:
        name: The ID name for the resource path.
        display_name: The name shown to users.
        description: A summary of what this resource is.
        mime_type: The format type like application/json.
        func: The function to get the data.
    """

    name: str
    display_name: str
    description: str
    mime_type: str
    func: Callable[[], Any]
