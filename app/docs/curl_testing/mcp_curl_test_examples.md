# MCP curl testing

Use these commands against the running MCP/HTTP server started with `python main.py` (defaults to `http://localhost:8003`).

The server speaks MCP protocol **2026-07-28 only**. That protocol is stateless: there is no `initialize` handshake and no `Mcp-Session-Id`. Instead, every request carries:

- the `MCP-Protocol-Version: 2026-07-28` header
- an `Mcp-Method` header matching the JSON-RPC `method` (plus `Mcp-Name` for `tools/call`, `prompts/get` and `resources/read`)
- a `_meta` object in `params` with the protocol version and client capabilities

The MCP endpoints do **not** require auth headers; the plain HTTP conversion routes can optionally accept an `Authorization: Bearer <token>` header (sample tokens are shown below)

**curl flag cheat sheet**

- `-s` Silent mode (hides progress meter/errors; add `-v` when debugging)
- `-N` Disable output buffering (needed for event-stream bodies)
- `-v` Verbose connection/debug output
- `-L` Follow redirects (helpful if you forget the trailing slash on `/mcp/`)

## Setup (run this first)

Paste this into your shell (bash or zsh). It defines the shared headers and an `mcp` helper that adds the required headers and `_meta` to every request.

```bash
BASE=${BASE:-http://localhost:8003}
MCP=${MCP:-$BASE/mcp/}
AUTH="Authorization: Bearer 143f4a46d74fee0d7918b2857577868cb3daf9e6e50ee91c2f7975ba26fdb8f7"
ACCEPT="Accept: application/json, text/event-stream"
PROTO="MCP-Protocol-Version: 2026-07-28"

# Usage: mcp <method> [params-without-braces] [name-for-Mcp-Name-header]
mcp() {
  local method="$1" args="${2:-}" name="${3:-}"
  local meta='"_meta":{"io.modelcontextprotocol/protocolVersion":"2026-07-28","io.modelcontextprotocol/clientCapabilities":{},"io.modelcontextprotocol/clientInfo":{"name":"curl","version":"1.0"}}'
  local params="{${args:+$args,}$meta}"
  local -a headers=(-H "Content-Type: application/json" -H "$ACCEPT" -H "$PROTO" -H "Mcp-Method: $method")
  [ -n "$name" ] && headers+=(-H "Mcp-Name: $name")
  curl -s "$MCP" "${headers[@]}" \
    -d "{\"jsonrpc\":\"2.0\",\"id\":1,\"method\":\"$method\",\"params\":$params}"
  echo
}
```

## Reusable developer workflow commands

A quick smoke test of the server and the MCP endpoint:

```bash
# 1. Check server health
curl -s "$BASE/health"

# 2. Discover the server: supported versions, capabilities, server info
mcp server/discover

# 3. List available MCP tools
mcp tools/list
```

- If you see `Connection refused`, the server/port is wrong. Update `BASE`.
- If you get an HTTP 307 redirect, keep the trailing slash or add `-L` to follow it automatically.
- If you get a response but no body, remove `-s` from the helper or add `-v` while debugging.

## 1. Discovery

```bash
mcp server/discover
```

`result.supportedVersions` should be `["2026-07-28"]`.

## 2. List and call tools

- List tools

```bash
mcp tools/list
```

- Call `convert_miles_to_kilometers` (shows validation if negative)

```bash
mcp tools/call '"name":"convert_miles_to_kilometers","arguments":{"miles":3.1}' convert_miles_to_kilometers
```

## 3. Resources

- List resources

```bash
mcp resources/list
```

- Read `resource://converter/unit_reference`

```bash
mcp resources/read '"uri":"resource://converter/unit_reference"' resource://converter/unit_reference
```

## 4. Prompts

- List prompts

```bash
mcp prompts/list
```

- Get `explain_conversion` (fills template arguments)

```bash
mcp prompts/get '"name":"explain_conversion","arguments":{"input_value":"100","input_unit":"celsius","target_unit":"fahrenheit"}' explain_conversion
```

## 5. Optional plain HTTP endpoint checks

These hit the FastAPI routes directly. Include the `Authorization` header only if your environment enforces it; the sample server accepts requests without it by default.

```bash
# Miles -> km with token JSON Body
curl -s -X POST "$BASE/convert-miles-to-kilometers" \
  -H "Content-Type: application/json" \
  -H "$AUTH" \
  -d '{"miles": 3.1}'
```

Each command returns JSON (tools/resources/prompts over MCP) or plain text/JSON (HTTP endpoints). Adjust `BASE`, `MCP`, or bearer token if you run the server on a different host/port.

## Troubleshooting tips

- Confirm the server log shows `Starting the Unit Converter API server...` and the port matches `BASE`.
- `-32022 Only MCP protocol 2026-07-28 is supported`: the client sent the old `initialize` handshake. Older (pre-2026) clients are not supported.
- `-32602 params._meta must be an object ...`: the request is missing `_meta`. Use the `mcp` helper.
- `-32020 ... header does not match ...`: the `Mcp-Method`, `Mcp-Name` or `MCP-Protocol-Version` header disagrees with the request body.
- If you’re on Windows PowerShell, replace single quotes with double quotes and escape inner quotes.
