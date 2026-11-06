"""Protocol lifecycle for MCP 2026-07-28: discovery and version enforcement (#126)."""

from tests.mcp.conftest import parse_mcp_response, request_meta

UNSUPPORTED_PROTOCOL_VERSION = -32022
INVALID_PARAMS = -32602
HEADER_MISMATCH = -32020
LEGACY_VERSION = "2025-11-25"


def test_server_discover(mcp_client, protocol_version):
    response = mcp_client.rpc("server/discover", id=1)

    assert response.status_code == 200  # noqa: PLR2004
    body = parse_mcp_response(response)
    print(f"[test_server_discover] body={body}")
    result = body["result"]
    assert result["supportedVersions"] == [protocol_version]
    assert "tools" in result["capabilities"]
    assert result["resultType"] == "complete"
    assert result["_meta"]["io.modelcontextprotocol/serverInfo"]["name"]


def test_legacy_initialize_rejected(
    mcp_url, mcp_headers, http_client, protocol_version
):
    headers = dict(mcp_headers, **{"MCP-Protocol-Version": LEGACY_VERSION})
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": LEGACY_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "pytest-legacy", "version": "1.0"},
        },
    }

    response = http_client.post(mcp_url, json=payload, headers=headers)

    body = parse_mcp_response(response)
    print(f"[test_legacy_initialize_rejected] body={body}")
    assert "result" not in body
    assert body["error"]["code"] == UNSUPPORTED_PROTOCOL_VERSION
    assert protocol_version in body["error"]["data"]["supported"]


def test_request_without_meta_rejected(mcp_url, mcp_headers, http_client):
    headers = dict(mcp_headers, **{"Mcp-Method": "tools/list"})
    payload = {"jsonrpc": "2.0", "id": 1, "method": "tools/list", "params": {}}

    response = http_client.post(mcp_url, json=payload, headers=headers)

    body = parse_mcp_response(response)
    print(f"[test_request_without_meta_rejected] body={body}")
    assert body["error"]["code"] == INVALID_PARAMS


def test_version_header_mismatch_rejected(mcp_client):
    meta = dict(request_meta(LEGACY_VERSION))

    response = mcp_client.rpc("tools/list", {"_meta": meta}, id=1)

    body = parse_mcp_response(response)
    print(f"[test_version_header_mismatch_rejected] body={body}")
    assert body["error"]["code"] == HEADER_MISMATCH
