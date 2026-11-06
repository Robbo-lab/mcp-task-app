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
- Optional, for the MCP Inspector: Node.js 22.23.4+, 24.22.1+ or 26.12.1+ (see [Inspect with the MCP Inspector](#inspect-with-the-mcp-inspector)).

## Setup from this folder

You can use either plain Python (venv + pip) or [uv](https://docs.astral.sh/uv/).

**Option A: Python venv + pip**

```bash
python -m venv .venv

# activate it: macOS / Linux / Git Bash
source .venv/bin/activate

# activate it: Windows PowerShell
.venv\Scripts\Activate.ps1

# then, on every OS
python -m pip install -r requirements.txt       # run the app
python -m pip install -r requirements-dev.txt   # also run the tests and linters
```

**Option B: uv**

```bash
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

The server reads `GEMINI_API_KEY` from the environment at startup; it does not load `.env` by itself. Load `.env` into the environment when you start it:

**With Python (venv activated)**

```bash
# macOS / Linux / Git Bash (bash or zsh)
set -a; source .env; set +a
python main.py
```

```powershell
# Windows PowerShell
Get-Content .env | Where-Object { $_ -match '^\s*[^#].*=' } | ForEach-Object {
  $name, $value = $_ -split '=', 2
  Set-Item -Path "env:$($name.Trim())" -Value $value.Trim()
}
python main.py
```

**With uv**

```bash
uv run --env-file .env python main.py
```

**Without a Gemini key** (conversion and task tools only), any of these work: `python main.py`, `python -m main`, `uv run main.py`, or `just run` (uses uv if it's installed, otherwise the activated venv's `python`).

If Gemini calls fail with `No client registered for provider: gemini`, the server was started without the key. See [`USAGE.md`](USAGE.md) for the full walkthrough.

**To run test curl commands see `app/docs/curl_testing/mcp_curl_test_examples.md`.**

**To run the server with your Gemini key and test it end to end, see [`USAGE.md`](USAGE.md).**

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

## Inspect with the MCP Inspector

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) lets you explore the server's tools, resources and prompts in a browser. Start the server first (see above), then:

```bash
npx @modelcontextprotocol/inspector@latest --web \
  --server-url http://localhost:8003/mcp/ --transport http --protocol-era modern
```

`--protocol-era modern` is required. The Inspector defaults to the older handshake protocol, which this server refuses with `Only MCP protocol 2026-07-28 is supported`.

To call the server from the terminal instead of the browser, use `--cli` with a `--method`:

```bash
npx @modelcontextprotocol/inspector@latest --cli \
  --server-url http://localhost:8003/mcp/ --transport http --protocol-era modern \
  --method tools/list
```

See [`USAGE.md`](USAGE.md#6-explore-with-the-mcp-inspector) for more Inspector commands.

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

**To run test curl commands see `app/docs/curl_testing/mcp_curl_test_examples.md`.**

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
