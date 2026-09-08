# MCP curl testing

Use these commands against the running MCP/HTTP server started with `python main.py` (defaults to `http://localhost:8003`).

The MCP endpoints do **not** require auth headers; the plain HTTP conversion routes can optionally accept an `Authorization: Bearer <token>` header (sample tokens are shown below)

**curl flag cheat sheet**

- `-s` Silent mode (hides progress meter/errors; add `-v` when debugging)
- `-D -` Write response headers to stdout (used to capture `mcp-session-id`)
- `-o /dev/null` Discard response body while keeping headers
- `-N` Disable output buffering (needed for event-stream bodies)
- `-v` Verbose connection/debug output
- `-L` Follow redirects (helpful if you forget the trailing slash on `/mcp/`)

```bash
# Optional helpers
BASE="http://localhost:8003" && \
MCP="$BASE/mcp/" && \
SSE="$BASE/sse/" && \
AUTH="Authorization: Bearer 143f4a46d74fee0d7918b2857577868cb3daf9e6e50ee91c2f7975ba26fdb8f7" && \
ACCEPT="Accept: application/json, text/event-stream" && \
PROTO="MCP-Protocol-Version: 2025-06-18"

```

## Reusable developer workflow commands

These commands provide a quick smoke-test workflow for developers who want to verify the server, MCP endpoint, and direct HTTP routes from the terminal.

```bash
# Base URLs
BASE=${BASE:-http://localhost:8003}
MCP=${MCP:-$BASE/mcp/}

# Shared MCP headers
ACCEPT="Accept: application/json, text/event-stream"
PROTO="MCP-Protocol-Version: 2025-06-18"

# 1. Check server health
curl -s "$BASE/health"

# 2. Start an MCP session and capture the session id
SESSION=$(curl -sD - -o /dev/null "$MCP" \
  -H "Content-Type: application/json" \
  -H "$ACCEPT" \
  -H "$PROTO" \
  -d '{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl","version":"1.0"}}}' \
  | awk 'BEGIN{IGNORECASE=1} /^mcp-session-id:/ {sub(/\r$/,""); print $2}')

# 3. List available MCP tools
curl -s "$MCP" \
  -H "Content-Type: application/json" \
  -H "$ACCEPT" \
  -H "$PROTO" \
  -H "Mcp-Session-Id: $SESSION" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
```

## Quick connectivity + session capture (run this first)

```bash
SESSION=$(curl -sD - -o /dev/null "$MCP" -H "Content-Type: application/json" -H "$ACCEPT" -H "$PROTO" -d '{"jsonrpc":"2.0","id":0,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{},"clientInfo":{"name":"curl","version":"1.0"}}}' | awk 'BEGIN{IGNORECASE=1} /^mcp-session-id:/ {sub(/\r$/,""); print $2}')
echo "SESSION=$SESSION"
```

- If you see `Connection refused`, the server/port is wrong. Update `BASE`.
- If you get an HTTP 307 redirect, keep the trailing slash or add `-L` to follow it automatically.
- If you get a response but no body, remove `-s` from the commands below or keep `-v` while debugging.
- If `SESSION` prints empty, rerun with `-v` to ensure the header is present.

## 1. MCP handshake

```bash
curl -s "$MCP" -H "Content-Type: application/json" -H "$ACCEPT" -H "$PROTO" -H "Mcp-Session-Id: $SESSION" -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"2025-06-18","capabilities":{"roots":{"listChanged":true}},"clientInfo":{"name":"curl","version":"1.0"}}}'
```

## 2. List and call tools

- List tools

```bash
curl -s "$MCP" -H "Content-Type: application/json" -H "$ACCEPT" -H "$PROTO" -H "Mcp-Session-Id: $SESSION" -d '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}'
```

- Call `miles_to_kilometers` (shows validation if negative)

```bash
curl -s "$MCP" -H "Content-Type: application/json" -H "$ACCEPT" -H "$PROTO" -H "Mcp-Session-Id: $SESSION" -d '{"jsonrpc":"2.0","id":4,"method":"tools/call","params":{"name":"miles_to_kilometers_miles_to_kilometers_post","arguments":{"miles":3.1}}}'
```

## 3. Resources

- List resources

```bash
curl -s "$MCP" -H "Content-Type: application/json" -H "$ACCEPT" -H "$PROTO" -H "Mcp-Session-Id: $SESSION" -d '{"jsonrpc":"2.0","id":5,"method":"resources/list","params":{}}'
```

- Read `resource://unit_reference`

```bash
curl -s "$MCP" -H "Content-Type: application/json" -H "$ACCEPT" -H "$PROTO" -H "Mcp-Session-Id: $SESSION" -d '{"jsonrpc":"2.0","id":6,"method":"resources/read","params":{"uri":"resource://unit_reference"}}'
```

## 4. Prompts

- List prompts

```bash
curl -s "$MCP" -H "Content-Type: application/json" -H "$ACCEPT" -H "$PROTO" -H "Mcp-Session-Id: $SESSION" -d '{"jsonrpc":"2.0","id":8,"method":"prompts/list","params":{}}'
```

- Get `explain_conversion` (fills template arguments)

```bash
curl -s "$MCP" -H "Content-Type: application/json" -H "$ACCEPT" -H "$PROTO" -H "Mcp-Session-Id: $SESSION" -d '{"jsonrpc":"2.0","id":9,"method":"prompts/get","params":{"name":"explain_conversion",
    "arguments": {
        "input_value": "100",
        "input_unit": "celsius",
        "target_unit": "fahrenheit"
      }
}}'
```

- Get `prompt list`

```bash
curl -s "$MCP" -H "Content-Type: application/json" -H "$ACCEPT" -H "$PROTO" -H "Mcp-Session-Id: $SESSION" -d '{"jsonrpc":"2.0","id":10,"method":"prompts/get","params":{"name":"api_usage","arguments":{}}}'
```

## 5. Optional plain HTTP endpoint checks

These hit the FastAPI routes directly. Include the `Authorization` header only if your environment enforces it; the sample server accepts requests without it by default.

```bash
# Miles -> km with token JSON Body
curl -s -X POST "$BASE/miles-to-kilometers" \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d '{"miles": 3.1}'

# Celsius -> Fahrenheit
curl -s -X POST "$BASE/miles-to-km?distance=25" -H "$AUTH"
```

Each command returns JSON (tools/resources/prompts over MCP) or plain text/JSON (HTTP endpoints). Adjust `BASE`, `MCP`, or bearer token if you run the server on a different host/port.

## Troubleshooting tips

- Confirm the server log shows `Starting the Unit Converter API server...` and the port matches `BASE`.
- Try SSE transport if HTTP streaming misbehaves:  
  `curl -N "$SSE" -H "Content-Type: application/json" -H "Accept: text/event-stream" -d '{"jsonrpc":"2.0","id":11,"method":"tools/list"}'`
- If you’re on Windows PowerShell, replace single quotes with double quotes and escape inner quotes.

```bash
curl -s "$MCP" -H "Content-Type: application/json" -H "$ACCEPT" -H "$PROTO" -H "Mcp-Session-Id: $SESSION" -d '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name": "miles_to_kilometers_miles_to_kilometers_post","arguments":{"distance":25}}}'
```

```json
{
  "event": "message",
  "data": {
    "jsonrpc": "2.0",
    "id": 3,
    "result": {
      "content": [
        {
          "type": "text",
          "text": "Unknown tool: 'miles_to_kilometers_miles_to_kilometers_post'"
        }
      ],
      "isError": true
    }
  }
}
```
