# mcpb-build

Source for the Claude Desktop one-click install bundle (`.mcpb` file).

This is the [MCP Bundle / Desktop Extension](https://github.com/anthropics/dxt) format. The `.mcpb` file is a small zip archive with `manifest.json`, `pyproject.toml`, and the MCP server code. Claude Desktop opens it, asks the user to point at their downloaded `reddit.db`, sets up a uv-managed Python environment, and registers the server. No editing config files.

## Build

```bash
# From the repo root
cp server.py mcpb-build/src/server.py    # keep source in sync
npx -y --package=@anthropic-ai/mcpb mcpb validate mcpb-build/manifest.json
npx -y --package=@anthropic-ai/mcpb mcpb pack mcpb-build sibo-research-db-${VERSION}.mcpb
```

Then attach the resulting `.mcpb` file to a [GitHub release](https://github.com/toczix/sibo-research-db/releases).

## Why server type `uv`?

The [`uv` server type](https://github.com/anthropics/dxt/blob/main/MANIFEST.md#uv-runtime-v04) declares Python dependencies in `pyproject.toml` and lets Claude Desktop install them in a managed virtual environment on the user's machine. The alternative (`python` type) requires bundling all deps in the .mcpb itself, which bloats the file to ~5-10 MB and is platform-specific. `uv` keeps the bundle to ~10 KB and works on macOS, Linux, and Windows.

## Files

- `manifest.json` — extension metadata + MCP server config
- `pyproject.toml` — Python dependencies (mcp[cli])
- `.mcpbignore` — paths excluded from the packed bundle
- `src/server.py` — the actual MCP server code (mirrored from `../server.py`)
