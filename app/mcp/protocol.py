"""Restrict the MCP server to protocol 2026-07-28 (issue #126)."""

from typing import Any, override

from fastmcp.server.middleware import CallNext, Middleware, MiddlewareContext
from mcp.shared.exceptions import MCPError
from mcp.types import LATEST_PROTOCOL_VERSION, UNSUPPORTED_PROTOCOL_VERSION

SUPPORTED_PROTOCOL_VERSIONS = [LATEST_PROTOCOL_VERSION]


class ModernProtocolOnly(Middleware):
    """Reject the pre-2026 `initialize` handshake.

    FastMCP 4 serves both protocol eras and has no setting to turn the
    handshake era off. 2026-07-28 has no `initialize`, so refusing it
    blocks every older client.
    """

    @override
    async def on_initialize(
        self,
        context: MiddlewareContext[Any],
        call_next: CallNext[Any, Any],
    ) -> Any:
        """Refuse the handshake with `UnsupportedProtocolVersion` (-32022)."""
        params = getattr(context.message, "params", None)
        raise MCPError(
            code=UNSUPPORTED_PROTOCOL_VERSION,
            message=f"Only MCP protocol {LATEST_PROTOCOL_VERSION} is supported",
            data={
                "supported": SUPPORTED_PROTOCOL_VERSIONS,
                "requested": getattr(params, "protocol_version", None),
            },
        )
