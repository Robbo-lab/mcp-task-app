import json
import os
from collections.abc import Generator
from typing import Any

import httpx
import pytest

collect_ignore = ["test_explain_prompt.py", "test_usage_prompt.py"]


@pytest.fixture(scope="session")
def base_url() -> str:
    return os.getenv("MCP_BASE_URL", "http://localhost:8003").rstrip("/")


@pytest.fixture(scope="session")
def mcp_url(base_url: str) -> str:
    return f"{base_url}/mcp/"


@pytest.fixture(scope="session")
def protocol_version() -> str:
    return os.getenv("MCP_PROTOCOL_VERSION", "2025-06-18")


@pytest.fixture(scope="session")
def mcp_headers(protocol_version: str) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": protocol_version,
    }


@pytest.fixture(scope="session")
def http_client() -> Generator[httpx.Client, None, None]:
    with httpx.Client(timeout=10.0) as client:
        yield client


class MCPTestClient:
    def __init__(self, client, url, headers):
        self.client = client
        self.url = url
        self.headers = dict(headers)
        self.session_id = None

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
            raise TypeError(f"Unexpected keyword arguments: {", ".join(kwargs)}")

        payload: dict[str, Any] = {"jsonrpc": "2.0", "id": rpc_id, "method": method}
        if params is not None:
            payload["params"] = params

        response = self.client.post(self.url, json=payload, headers=self.headers)
        sid = response.headers.get("mcp-session-id")
        if sid:
            self.session_id = sid
            self.headers["Mcp-Session-Id"] = sid
        return response

    def notification(self, method: str, params: dict | None = None):
        payload: dict[str, Any] = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        return self.client.post(self.url, json=payload, headers=self.headers)


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
    client = MCPTestClient(http_client, mcp_url, mcp_headers)

    init_response = client.rpc(
        "initialize",
        {
            "protocolVersion": protocol_version,
            "capabilities": {},
            "clientInfo": {"name": "pytest", "version": "1.0"},
        },
        rpc_id=0,
    )
    assert init_response.status_code in {200, 202}

    client.notification("notifications/initialized")
    return client
