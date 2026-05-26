<p align="center">
  <img src="banner.png" alt="Sibo Research Database — Chat with 7 million real patient experiences from 18 health subreddits" width="100%" />
</p>

# Sibo Reddit Research Database

### Chat with 7 million real patient experiences from 18 health subreddits — find what's actually working for symptoms like yours.

A research tool for chronic illness patients. Searches **7 million real patient comments** across 18 health subreddits — SIBO, MCAS, IBS, long covid, dysautonomia, mold, histamine, and more.

> **Not medical advice.** This is patient-reported data from public Reddit posts. Use it to find patterns and leads worth bringing to your doctor — never to diagnose or treat yourself.

---

## Install in 3 steps

**Step 1 — Copy this prompt into Claude Code or Codex CLI:**

```
https://github.com/toczix/sibo-research-db
https://huggingface.co/datasets/toczix/sibo-research-db

I want to chat with this database for my SIBO-related symptoms. Please
install it for me — follow the README in the GitHub repo.
```

**Step 2** — Wait for it to finish (it downloads a 5.4 GB database — go make coffee).

**Step 3** — Restart your AI tool. Start asking questions about your symptoms.

That's it. The AI reads the README, clones the repo, downloads the database, configures itself, and verifies it works.

### Don't have Claude Code or Codex?

If you have **Claude Desktop**, there's a one-click install:

1. [Download the .mcpb extension](https://github.com/toczix/sibo-research-db/releases/latest) (file ending in `.mcpb`)
2. [Download the database](https://huggingface.co/datasets/toczix/sibo-research-db/resolve/main/reddit.db) (5.4 GB)
3. Double-click the `.mcpb` — Claude Desktop opens an install dialog. Point it at your `reddit.db`.
4. Restart Claude Desktop.

If you'd rather configure things by hand, see [Developer setup](#developer-setup) at the bottom.

---

## What's in the database

| Subreddit | Topic | Comments |
|---|---|---:|
| r/covidlonghaulers | Long COVID | 1,883,928 |
| r/Supplements | Supplement protocols | 894,256 |
| r/ibs | Irritable bowel syndrome | 892,121 |
| r/SIBO | Small intestinal bacterial overgrowth | 710,128 |
| r/MCAS | Mast cell activation, histamine reactions | 558,683 |
| r/dysautonomia | POTS, autonomic issues | 433,599 |
| r/Microbiome | Gut microbiome | 313,367 |
| r/LongCovid | Long COVID (different community) | 257,465 |
| r/Candida | Candida overgrowth | 251,539 |
| r/FODMAPS | Low-FODMAP diet | 249,222 |
| r/HistamineIntolerance | Histamine reactions | 227,376 |
| r/FoodAllergies | Food sensitivities | 203,735 |
| r/ToxicMoldExposure | Mold illness / CIRS | 188,293 |
| r/GutHealth | General gut health | 57,892 |
| r/Longcovidgutdysbiosis | LC + gut overlap | 36,437 |
| r/FunctionalMedicine | Functional medicine | 28,322 |
| r/LeakyGutSyndrome | Intestinal permeability | 11,890 |
| r/SiboSuccessStories | Recovery stories (small but high signal) | 7,301 |

**18 subreddits. 695,050 posts. 7,205,554 comments.** Coverage roughly the start of each subreddit through May 2026.

---

## Optional: layer your personal notes

If you keep your own research document (symptom timeline, test results, treatment hypotheses), you can expose it to the AI as an extra tool. Add these env vars to your AI tool's MCP config:

```
SIBO_REPORT=/path/to/your/research.md
SIBO_SYMPTOMS=/path/to/your/symptoms.md
```

When set, the AI gets two extra tools — `get_report` and `get_symptoms` — that read your local files. Useful for asking *"given my symptom profile and the database, what hasn't been tried yet?"* without pasting your notes every conversation. Without those env vars, nothing personal is exposed.

---

## If something goes wrong

**The AI says "database not found".** The install dialog or AI agent needs to know where you put `reddit.db`. Re-run the install prompt and tell it where the file is.

**Database download keeps failing.** Try the smaller compressed version: [reddit.db.zst](https://huggingface.co/datasets/toczix/sibo-research-db/resolve/main/reddit.db.zst) (1.86 GB). You'll need `zstd` installed (`brew install zstd` on Mac, `apt install zstd` on Linux, [download for Windows](https://github.com/facebook/zstd/releases)).

**The `.mcpb` won't install in Claude Desktop.** Update Claude Desktop to 0.10 or newer.

**Anything else.** [Open an issue](https://github.com/toczix/sibo-research-db/issues) — include which AI tool you're using and what you saw.

---

## 🤖 If you're an AI agent reading this to install for a user

You're being asked to install this MCP server. Here is the exact procedure:

1. **Verify prerequisites:**
   - `python3 --version` — must be 3.10+
   - `uv --version` — install if missing with `curl -LsSf https://astral.sh/uv/install.sh | sh`
   - Confirm 7+ GB of free disk

2. **Pick an install location.** Default to `~/sibo-research-db` unless the user specifies. Confirm with the user before downloading.

3. **Clone the repo:**
   ```
   git clone https://github.com/toczix/sibo-research-db.git ~/sibo-research-db
   ```

4. **Download the database** (5.4 GB, may take 10-30 min depending on connection):
   ```
   curl -L --fail --retry 3 -o ~/sibo-research-db/reddit.db \
     https://huggingface.co/datasets/toczix/sibo-research-db/resolve/main/reddit.db
   ```
   If the user has zstd installed and wants a faster download, use `reddit.db.zst` instead (1.86 GB) and decompress with `zstd -d`.

5. **Verify integrity:**
   ```
   shasum -a 256 ~/sibo-research-db/reddit.db
   ```
   Expected: `a313e5313bd0b4ece33961340b7c4fdc93dd16976bcc2e0580f818b253a36f09`

6. **Install dependencies:**
   ```
   cd ~/sibo-research-db && uv sync
   ```

7. **Smoke test:**
   ```
   uv run python search.py stats
   ```
   Should print subreddit counts. If it errors, do not proceed — diagnose first.

8. **Register the MCP server** with the host AI tool:
   - **Claude Code:** `claude mcp add --transport stdio --scope user sibo-research-db -- uv --directory ~/sibo-research-db run python server.py`
   - **Codex CLI:** `codex mcp add sibo-research-db -- uv --directory ~/sibo-research-db run python server.py`
   - **Cursor / Cline / Claude Desktop:** edit the appropriate config file (see Developer Setup below).

9. **Tell the user:** "Installed. Restart your AI tool, then ask me a question about your symptoms."

If any step fails, report the actual error to the user — do not silently retry past 3 attempts.

---

# Developer setup

The sections below assume comfort with terminals and config files. Skip if you used one of the install paths above.

## Prerequisites

- **Python 3.10+** (3.11+ recommended)
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)**:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **~7 GB free disk** (5.4 GB for the database + working room)

## Manual install

```bash
git clone https://github.com/toczix/sibo-research-db.git
cd sibo-research-db

uv tool install huggingface_hub
hf download toczix/sibo-research-db reddit.db --repo-type dataset --local-dir .

uv sync
uv run python search.py stats
uv run python search.py search "ginger AND artichoke" --limit 3
```

## Setup: Claude Desktop (manual JSON)

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "sibo-research-db": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/sibo-research-db", "run", "python", "server.py"]
    }
  }
}
```

If Claude Desktop can't find `uv`, use the full path (`which uv`).

## Setup: Claude Code

```bash
claude mcp add --transport stdio --scope user sibo-research-db \
  -- uv --directory /absolute/path/to/sibo-research-db run python server.py
claude mcp list
```

## Setup: Codex CLI

```bash
codex mcp add sibo-research-db \
  -- uv --directory /absolute/path/to/sibo-research-db run python server.py
```

Or edit `~/.codex/config.toml`:

```toml
[mcp_servers.sibo-research-db]
command = "uv"
args = ["--directory", "/absolute/path/to/sibo-research-db", "run", "python", "server.py"]
```

## Setup: Cursor

`~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (per-project):

```json
{
  "mcpServers": {
    "sibo-research-db": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/sibo-research-db", "run", "python", "server.py"]
    }
  }
}
```

## Setup: VS Code Copilot Agent

`.vscode/mcp.json` (workspace) or `~/.config/Code/User/mcp.json` (global):

```json
{
  "servers": {
    "sibo-research-db": {
      "type": "stdio",
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/sibo-research-db", "run", "python", "server.py"]
    }
  }
}
```

## CLI usage (no AI)

```bash
uv run python search.py stats
uv run python search.py search "rifaximin AND biofilm" --limit 10
uv run python search.py thread 1jyj8vp
uv run python search.py export "POIS" -o pois_results.jsonl
```

## Tools available to the AI

Public (10): `stats`, `list_subreddits`, `search`, `get_thread`, `get_post`, `get_top_posts`, `count_mentions`, `compare_mentions`, `find_active_voices`, `sql_query`.

Optional (2, gated on env vars): `get_report`, `get_symptoms` — read your local Markdown notes.

## Safety

- SQLite opens read-only (`mode=ro&immutable=1` + `PRAGMA query_only=ON`) — writes physically can't happen
- All limit parameters clamped to bounded ranges
- `sql_query` streams via `fetchmany()`, capped at 200 rows
- `find_active_voices` includes a "do not contact" warning in its response

## Verify the database

```bash
sqlite3 reddit.db "PRAGMA integrity_check;"   # should print "ok"
shasum -a 256 reddit.db                       # compare against checksums.txt on HF
```

## Build it yourself (fresher data, more subs)

```bash
# Edit download_subreddits.py to change the SUBREDDITS list, then:
python download_subreddits.py NewSubreddit
python ingest_all.py
```

Downloads pull from [arctic-shift](https://arctic-shift.photon-reddit.com).

## Build the Claude Desktop extension

```bash
./scripts/build-mcpb.sh
```

Produces `sibo-research-db-${VERSION}.mcpb`. Attach to a GitHub release.

---

## License

**Code:** MIT (see [LICENSE](LICENSE)).

**Reddit content** is owned by its original authors and Reddit. Redistributed from the public [arctic-shift](https://arctic-shift.photon-reddit.com) archive for research and education. Not a claim of public-domain status. If you're a Reddit user whose content is included and want it removed from future updates, open an issue.
