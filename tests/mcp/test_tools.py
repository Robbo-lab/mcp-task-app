from tests.mcp.conftest import parse_mcp_response


def test_tools_list(mcp_client):
    response = mcp_client.rpc("tools/list", {}, id=2)

    assert response.status_code == 200  # noqa: PLR2004
    body = parse_mcp_response(response)
    print(f"[test_tools_list] status_code={response.status_code}")
    print(f"[test_tools_list] body={body}")
    assert body["jsonrpc"] == "2.0"
    assert "result" in body
    assert "tools" in body["result"]

    tools = body["result"]["tools"]
    print(f"[test_tools_list] tools={tools}")
    assert isinstance(tools, list)
    assert len(tools) > 0
    assert all("name" in tool for tool in tools)
    assert all("description" in tool for tool in tools)


def test_tools_call_miles_to_km(mcp_client):
    response = mcp_client.rpc(
        "tools/call",
        {
            "name": "convert_miles_to_kilometers",
            "arguments": {"miles": 77},
        },
        id=3,
    )

    assert response.status_code == 200  # noqa: PLR2004
    body = parse_mcp_response(response)
    print(f"[test_tools_call_miles_to_km] status_code={response.status_code}")
    print(f"[test_tools_call_miles_to_km] body={body}")
    assert "result" in body
    assert "error" not in body

    result = body["result"]
    print(f"[test_tools_call_miles_to_km] result={result}")
    assert isinstance(result, dict)
    assert "content" in result or "structuredContent" in result


def test_tool_names(mcp_client):
    """
    Test that asserts the exact tool names from tools/list.
    """
    response = mcp_client.rpc("tools/list", {}, id=2)
    assert response.status_code == 200  # noqa: PLR2004

    body = parse_mcp_response(response)
    tools = body["result"]["tools"]

    expected_tool_names = {
        "get_task_by_name",
        "get_task_by_id",
        "delete_task_by_name",
        "create_task",
        "filter_task_by_type",
        "complete_task",
        "generate_content",
        "convert_miles_to_kilometers",
        "get_job_status",
        "root",
        "health_health_get",
        "generate_async_v1_llm_enqueue_post",
    }

    #  get_job_status, root, health_health_get,
    #  generate_async_v1_llm_enqueue_post
    #  These four additional tools are currently exposed.
    # Remove them from this set once their exposure is resolved under #130.

    actual_tool_names = {tool["name"] for tool in tools}

    assert actual_tool_names == expected_tool_names
    assert len(actual_tool_names) == len(tools)
