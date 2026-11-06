import json
import os
from collections.abc import Generator
from typing import Any

import httpx
import pytest

collect_ignore = ["test_explain_prompt.py", "test_usage_prompt.py"]

PROTOCOL_VERSION_KEY = "io.modelcontextprotocol/protocolVersion"
CLIENT_CAPABILITIES_KEY = "io.modelcontextprotocol/clientCapabilities"
CLIENT_INFO_KEY = "io.modelcontextprotocol/clientInfo"


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("MCP_BASE_URL", "http://localhost:8003").rstrip("/")


@pytest.fixture(scope="session")
def mcp_url(base_url: str) -> str:
    return f"{base_url}/mcp/"


@pytest.fixture(scope="session")
def protocol_version() -> str:
    return os.getenv("MCP_PROTOCOL_VERSION", "2026-07-28")


@pytest.fixture(scope="session")
def mcp_headers(protocol_version: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": protocol_version,
    }


@pytest.fixture(scope="session")
def http_client() -> Generator[httpx.Client]:
    with httpx.Client(timeout=10.0) as client:
        yield client


def request_meta(protocol_version: str) -> dict[str, Any]:
    """Build the per-request `_meta` envelope that MCP 2026-07-28 requires."""
    return {
        PROTOCOL_VERSION_KEY: protocol_version,
        CLIENT_CAPABILITIES_KEY: {},
        CLIENT_INFO_KEY: {"name": "pytest", "version": "1.0"},
    }


def request_headers(
    base_headers: dict[str, str], method: str, params: dict[str, Any]
) -> dict[str, str]:
    """Add the `Mcp-Method` / `Mcp-Name` headers Streamable HTTP requires."""
    headers = dict(base_headers)
    headers["Mcp-Method"] = method
    name = params.get("name") or params.get("uri")
    if name:
        headers["Mcp-Name"] = str(name)
    return headers


class MCPTestClient:
    """Stateless MCP 2026-07-28 client: no handshake, no session id."""

    def __init__(self, client, url, headers, protocol_version):
        self.client = client
        self.url = url
        self.headers = dict(headers)
        self.protocol_version = protocol_version

    def rpc(
        self,
        method: str,
        params: dict | None = None,
        rpc_id: int | str = 1,
        **kwargs: Any,
    ):
        if "id" in kwargs:
            rpc_id = kwargs.pop("id")
        if kwargs:
            raise TypeError(f"Unexpected keyword arguments: {', '.join(kwargs)}")

        params = dict(params or {})
        params.setdefault("_meta", request_meta(self.protocol_version))
        payload: dict[str, Any] = {
            "jsonrpc": "2.0",
            "id": rpc_id,
            "method": method,
            "params": params,
        }
        headers = request_headers(self.headers, method, params)
        return self.client.post(self.url, json=payload, headers=headers)


def parse_mcp_response(response: httpx.Response) -> dict:
    content_type = response.headers.get("content-type", "")
    if "text/event-stream" not in content_type:
        return response.json()

    for line in response.text.splitlines():
        if line.startswith("data:"):
            return json.loads(line.removeprefix("data:").strip())

    raise ValueError("No SSE data line found in MCP response")


@pytest.fixture
def mcp_client(http_client, mcp_url, mcp_headers, protocol_version):
    return MCPTestClient(http_client, mcp_url, mcp_headers, protocol_version)
