# Converter API + MCP

- builds the FastAPI app, wraps it with FastMCP, mounts MCP HTTP/SSE endpoints, registers resources and prompts, and starts uvicorn.
- requirements.txt - Python dependencies.

## System Architecture

This project uses `main.py` as the main entry point.

The FastAPI app provides the HTTP API, documentation pages, and health check. FastMCP wraps the FastAPI app and exposes MCP tools, resources, and prompts through the MCP endpoint.

```txt
main.py
  |
  |-- FastAPI app
  |     |-- HTTP routes
  |     |-- Swagger UI
  |     |-- ReDoc
  |     |-- health check
  |
  |-- FastMCP
        |-- MCP tools
        |-- MCP resources
        |-- MCP prompts
        |-- /mcp endpoint
```

Important folders:

```txt
app/mcp/mcp_tools/        # MCP tools and FastAPI route logic
app/mcp/mcp_prompts/      # MCP prompt templates
app/mcp/mcp_resources/    # MCP resource definitions
tests/mcp/                # MCP test suite
example_llm_client/       # Example Gemini / LLM client
```

## Prerequisites

- Python 3.13
- Virtual environment.
- npm inspector below.

## Setup from this folder

```bash
python -m venv .venv

# Mac or Gitbash
source .venv/bin/activate

# Windows powershell:
.venv\Scripts\activate
python -m pip install -r requirements.txt

# or use UV:
uv sync
```

## Configure Gemini

The project includes an example environment file called `.env.example`.

Create a local `.env` file from `.env.example`, then add your Gemini configuration:

```env
GEMINI_API_KEY=your_api_key_here
GEMINI_MODEL=gemini-2.5-flash
MCP_SERVER_URL=http://localhost:8003/mcp
```

You can get a Gemini API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

The `.env` file is ignored by git, so your API key should stay local and should not be committed.

## Run the HTTP + MCP server

```bash
# start the server

# with Python 
python -m main

# with UV (recommended)
uv run main.py

# with just
just run
```

**To run test curl commands see** [mcp_curl_test_examples.md](app/docs/curl_testing/mcp_curl_test_examples.md).

You'll see:

- Swagger UI: http://localhost:8003/docs
- ReDoc: http://localhost:8003/redoc

MCP endpoints served by FastMCP:

- streamable-http: http://localhost:8003/mcp



Each endpoint returns JSON like:

- { "result": <number>, "operation": "..." } or { "error": "..." } for invalid input.

## Headers & Authentication (common to all)

### Add JSON content type (and optionally your auth token)

```txt
-H "Content-Type: application/json"
-H "Authorization: Bearer <TOKEN>"
```

Our server doesn't require auth yet, we can omit the **Authorization** header.

## Rate Limiting

The API includes rate limiting middleware for HTTP and MCP endpoints.

- Limit: 50 requests per client IP every 3600 seconds.
- Storage: request timestamps are tracked in memory and expired records are cleared.
- Exceeded limit: returns `429 Too Many Requests` with a `Retry-After` header.
- Missing client IP: returns `400 Bad Request`.

## Use with MCP (VS Code Example)

1. Start the server as above.
2. Point your MCP client to the process.

Example VS Code .vscode/mcp.json entry:
```json
{
  "servers": {
    "UnitConverter": {
      "command": "python",
      "args": ["main.py"]
    }
  }
}
```

3. From the MCP client, list artifacts. You should see:
   - Tools: celsius_to_fahrenheit, fahrenheit_to_celsius, kilometers_to_miles, miles_to_kilometers
   - Resources: resource://unit_reference, resource://troubleshooting_guide
   - Prompts: explain_conversion, api_usage

## Inspect with the npm MCP Inspector

- explore everything (tools, resources, prompts) in a browser.
- with the server already running on http://localhost:8003

```bash
# If env error appears
npx @modelcontextprotocol/inspector@latest -e DUMMY=1 --url http://localhost:8003/mcp --transport streamable-http
```

## Run Tests

Run the test suite:

```bash
python -m pytest -v
```

Or with UV:

```bash
uv run pytest -v
```

Or with just:

```bash
just test
```

## Adding Extensions

Add new MCP tools here:

```txt
app/mcp/mcp_tools/
```

Add new MCP prompts here:

```txt
app/mcp/mcp_prompts/
```

Add new MCP resources here:

```txt
app/mcp/mcp_resources/
```

Add or update MCP tests here:

```txt
tests/mcp/
```

Add or update example LLM client code here:

```txt
example_llm_client/
```

### Adding New MCP Tools

For details on MCP tools, see [mcp-tools-naming-guide.md](org/mcp-tools-naming-guide.md).

## Contributing

For detailed contribution guidelines, see [CONTRIBUTION.md](CONTRIBUTION.md).



## Handling errors

- Parse error (-32700)
- Invalid request (-32600)
- Method not found (-32601)
- Invalid params (-32602)
- Internal error (-32603)

## Notes

**To run test curl commands see** [mcp_curl_test_examples.md](app/docs/curl_testing/mcp_curl_test_examples.md).

macOS/Linux (bash/zsh)
- The examples above will work as-is.

```bash
# Windows PowerShell
curl -Method POST http://localhost:8003/mcp/ `  -Headers @{ "Content-Type"="application/json" }`
-Body '{"jsonrpc":"2.0","method":"prompts/list","params":{},"id":1}'
```

Windows CMD

```bash
curl -s -X POST http://localhost:8003/mcp/ -H "Content-Type: application/json" -d "{\"jsonrpc\":\"2.0\",\"method\":\"prompts/list\",\"params\":{},\"id\":1}"
```

---

## Tool Installation Notes

### Just Command Runner (Recommended)

This project uses `just` to simplify common tasks like running the server and tests.

### Recommended Installation

```bash
# Using UV (Any platform)
uv tool install rust-just
```

#### Windows

```powershell
# Using WinGet (Native)
winget install --id Casey.Just --exact

# Using Scoop
scoop install just

# Using Chocolatey
choco install just
```

#### macOS

```bash
# Using Homebrew (macOS)
brew install just
```

Once installed, simply run `just` in your terminal to see all available commands.
