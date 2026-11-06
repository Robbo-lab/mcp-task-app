# Usage: running the server and testing it with Gemini

This guide walks through running the server with a Google AI Studio (Gemini) API key and testing it at three levels: the REST routes, the MCP endpoint, and the example LLM client.

The MCP endpoint speaks protocol **2026-07-28 only**. That protocol is stateless: there is no `initialize` handshake and no session id, and every request carries its protocol version in headers and in `params._meta`. The curl helper in step 4 handles this for you.

## Prerequisites

- Python 3.13+
- Dependencies installed, with **either**:
  - **Python venv + pip:** `python -m venv .venv`, activate it (`source .venv/bin/activate`, or `.venv\Scripts\Activate.ps1` on Windows PowerShell), then `python -m pip install -r requirements.txt`
  - **[uv](https://docs.astral.sh/uv/):** `uv sync`
- A Gemini API key from [Google AI Studio → API keys](https://aistudio.google.com/app/apikey)

Each step below shows both options. With Python, run the commands in a terminal where the venv is activated.

## 1. Put your key in `.env`

```bash
cp .env.example .env
```

Edit `.env` and set:

```bash
GEMINI_API_KEY=<your key>
GEMINI_MODEL=gemini-2.5-flash
```

`.env` is gitignored. Never commit your key, paste it into issues or PRs, or type it on the command line (it ends up in your shell history).

## 2. Start the server with the key loaded

The server reads `GEMINI_API_KEY` from the environment when it starts; it does not load `.env` itself. Load `.env` into the environment as you start it.

**With Python (venv activated):**

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

`set -a; source .env` exports every variable in `.env` to the current terminal session only. Keep `.env` values unquoted and without spaces.

**With uv:**

```bash
uv run --env-file .env python main.py
```

The server listens on `http://localhost:8003`. Check it in a second terminal:

```bash
curl -s http://localhost:8003/health
```

If the key isn't loaded, every Gemini call returns `No client registered for provider: gemini`.

## 3. Test the REST routes

Synchronous generation:

```bash
curl -s -X POST http://localhost:8003/v1/llm/generate \
  -H "Content-Type: application/json" \
  -d '{"provider":"gemini","model":"gemini-2.5-flash","messages":[{"role":"user","content":"Convert 10 km to miles in one line."}]}'
```

Background generation (enqueue, then use the `job_id` it returns):

```bash
curl -s -X POST http://localhost:8003/v1/llm/enqueue \
  -H "Content-Type: application/json" \
  -d '{"provider":"gemini","model":"gemini-2.5-flash","messages":[{"role":"user","content":"Say hello."}]}'

curl -s http://localhost:8003/v1/llm/jobs/<job_id>
```

## 4. Test through MCP (protocol 2026-07-28)

Paste this setup into your shell (bash or zsh). It defines an `mcp` helper that adds the required headers and `_meta` to every request:

```bash
BASE=${BASE:-http://localhost:8003}
MCP=${MCP:-$BASE/mcp/}
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

Discover the server and list its tools:

```bash
mcp server/discover   # result.supportedVersions should be ["2026-07-28"]
mcp tools/list
```

Call Gemini through the MCP tool:

```bash
mcp tools/call '"name":"generate_sync_v1_llm_generate_post","arguments":{"provider":"gemini","model":"gemini-2.5-flash","messages":[{"role":"user","content":"Convert 10 km to miles in one line."}]}' generate_sync_v1_llm_generate_post
```

A working call returns `"isError": false`, with Gemini's reply in `content` and `structuredContent`.

> The tool keeps its auto-generated name until [#131](https://github.com/Robbo-lab/mcp-task-app/issues/131) renames it to `generate_content`. Run `mcp tools/list` to see the current names.

For more MCP calls (resources, prompts, the converter tool), see [`app/docs/curl_testing/mcp_curl_test_examples.md`](app/docs/curl_testing/mcp_curl_test_examples.md).

## 5. Run the example LLM client

Run it from the repo root so its `app.*` imports resolve. Unlike the server, the client reads `.env` itself, so no extra step is needed:

```bash
# With Python (venv activated)
python -m example_llm_client.simulated_llm_client

# With uv
uv run python -m example_llm_client.simulated_llm_client
```

The client doesn't connect to the MCP server. When Gemini asks for the conversion tool, the client prints a curl command for you to run, and you paste the result back in. The command looks like this:

```bash
curl -s -X POST http://localhost:8003/convert-miles-to-kilometers \
  -H "Content-Type: application/json" -d '{"miles": 10}'
```

## 6. Explore with the MCP Inspector

The [MCP Inspector](https://github.com/modelcontextprotocol/inspector) is the official tool for exploring an MCP server. It runs through `npx`, so you need Node.js (22.23.4+, 24.22.1+ or 26.12.1+), but neither uv nor Python. These commands were tested with Inspector 2.14.0.

**Always pass `--protocol-era modern`.** Without it, the Inspector uses the older handshake protocol, and this server refuses it with `Only MCP protocol 2026-07-28 is supported`.

### In the browser

```bash
npx @modelcontextprotocol/inspector@latest --web \
  --server-url http://localhost:8003/mcp/ --transport http --protocol-era modern
```

The Inspector prints a local URL like `http://127.0.0.1:6274?MCP_INSPECTOR_API_TOKEN=…`. Open the full URL, token included (the token stops other sites from using the Inspector). From there you can browse the tools, resources and prompts, and call them with a form. Press `Ctrl+C` to stop it. To test Gemini, call `generate_sync_v1_llm_generate_post` with `provider` `gemini`, `model` `gemini-2.5-flash` and a `messages` list. The server needs the key loaded (step 2).

### From the terminal

Use `--cli` with a `--method`. The output is JSON.

```bash
# List tools (swap in resources/list or prompts/list)
npx @modelcontextprotocol/inspector@latest --cli \
  --server-url http://localhost:8003/mcp/ --transport http --protocol-era modern \
  --method tools/list

# Call the converter tool
npx @modelcontextprotocol/inspector@latest --cli \
  --server-url http://localhost:8003/mcp/ --transport http --protocol-era modern \
  --method tools/call --tool-name convert_miles_to_kilometers --tool-arg miles=10

# Read a resource
npx @modelcontextprotocol/inspector@latest --cli \
  --server-url http://localhost:8003/mcp/ --transport http --protocol-era modern \
  --method resources/read --uri resource://converter/unit_reference
```

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `No client registered for provider: gemini` | The server started without `GEMINI_API_KEY` | Restart it with `.env` loaded (step 2): `set -a; source .env; set +a` then `python main.py`, or `uv run --env-file .env python main.py` |
| `401` / `403` / "API key not valid" | Wrong key, or the Gemini API isn't enabled for it | Check the key in AI Studio |
| `429` | Free-tier rate limit reached | Wait and retry; see [Gemini rate limits](https://ai.google.dev/gemini-api/docs/rate-limits) |
| `404` / "model not found" | The model name isn't available to your key | Change `GEMINI_MODEL` or the `model` in the request |
| `-32022 Only MCP protocol 2026-07-28 is supported` | The client sent the old `initialize` handshake | Use a 2026-07-28 client or the `mcp` helper above. For the MCP Inspector, add `--protocol-era modern` |
| `npm warn EBADENGINE Unsupported engine` | Your Node.js version is older than the Inspector supports | Upgrade Node.js to 22.23.4+, 24.22.1+ or 26.12.1+ |
| `-32602 params._meta must be an object ...` | The request is missing `_meta` | Use the `mcp` helper |
| `-32020 ... header does not match ...` | `Mcp-Method`, `Mcp-Name` or `MCP-Protocol-Version` disagrees with the request body | Use the `mcp` helper |
| `Connection refused` | The server isn't running, or `BASE` points at the wrong port | Start the server; check `BASE` |
