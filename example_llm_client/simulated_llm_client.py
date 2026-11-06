from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from dotenv import load_dotenv

from app.llm.base import BaseLLMClient, LLMRequest
from app.llm.providers.gemini.client import GeminiClient
from app.llm.providers.gemini.models import (
    GenerateContentRequest,
    is_function_call_part,
    is_text_part,
)

load_dotenv()

# Configuration
API_KEY = os.getenv("GEMINI_API_KEY")
MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


def get_available_tools() -> list[dict[str, Any]]:
    """Define the tools available to Gemini."""
    return [
        {
            "function_declarations": [
                {
                    "name": "miles_to_kilometers",
                    "description": "Convert miles to kilometers",
                    "parameters": {
                        "type": "object",
                        "properties": {"miles": {"type": "number"}},
                        "required": ["miles"],
                    },
                }
            ]
        }
    ]


async def perform_initial_turn(
    client: GeminiClient, query: str
) -> tuple[list[Any], Any]:
    """
    Execute the first turn using the Gemini-specific interface
    to support tool discovery.
    """
    messages: list[Any] = [{"role": "user", "parts": [{"text": query}]}]
    tools = get_available_tools()

    print("\n[Thinking...]")
    # Using the specific generate_content method for tool support
    response = await client.generate_content(
        GenerateContentRequest(contents=messages, tools=tools)  # type: ignore
    )
    return messages, response.candidates[0].content


def handle_manual_tool_call(call: Any) -> dict[str, Any]:
    """Prompt the user for manual tool execution."""
    print(f"\n[Tool Requested: {call.name}]")
    print("\n--- ACTION REQUIRED ---")
    print(
        "Run: curl -s -X POST http://localhost:8003/convert-miles-to-kilometers "
        f"-H 'Content-Type: application/json' -d '{json.dumps(call.args)}'"
    )

    mcp_result = input("Enter the 'result' from the tool: ")

    return {
        "role": "model",
        "parts": [
            {
                "functionResponse": {
                    "name": call.name,
                    "response": {"result": mcp_result},
                }
            }
        ],
    }


async def run_simple_demo(client: BaseLLMClient) -> None:
    """Demonstrates the provider-agnostic 'generate' method."""
    print("\n--- Provider-Agnostic Basic Call ---")
    user_query = "Hello, what LLM are you?"
    print(f"User: {user_query}")

    request = LLMRequest(prompt=user_query)
    response = await client.generate(request)

    print(f"Gemini: {response.text}")


async def run_mcp_demo(client: GeminiClient) -> None:
    """The main execution pipeline for the Gemini + MCP example."""
    print("\n--- Gemini MCP Simulation ---")
    user_query = input("User (e.g. 'what is 10 miles to km'): ")

    # 1. Start the conversation
    messages, model_turn = await perform_initial_turn(client, user_query)

    # 2. Process any tool requests
    for part in model_turn.parts:
        if is_function_call_part(part):
            tool_res_message = handle_manual_tool_call(part.function_call)

            messages.extend([model_turn.model_dump(by_alias=True), tool_res_message])

            # 3. Get the final explanation
            print("\n[Explaining...]")
            final_resp = await client.generate_content(
                GenerateContentRequest(contents=messages)
            )
            final_part = final_resp.candidates[0].content.parts[0]

            if is_text_part(final_part):
                print(f"\nGemini: {final_part.text}")
            return

    # If no tool was requested, just show the response
    if model_turn.parts and is_text_part(model_turn.parts[0]):
        print(f"\nGemini: {model_turn.parts[0].text}")


async def main_async() -> None:
    if not API_KEY:
        print("Error: GEMINI_API_KEY not found in .env")
        return

    # Create the client - notice we type it as the base interface where appropriate
    gemini_client = GeminiClient(api_key=API_KEY, model_name=MODEL)

    # Run the agnostic demo
    await run_simple_demo(gemini_client)

    # Run the specific MCP demo
    await run_mcp_demo(gemini_client)


if __name__ == "__main__":
    asyncio.run(main_async())
