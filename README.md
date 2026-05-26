# Sibo Reddit Research Database

### Chat with 7 million real patient experiences from 18 health subreddits — find what's actually working for symptoms like yours.

A research tool for chronic illness patients. Searches **7 million real patient comments** across 18 health subreddits — SIBO, MCAS, IBS, long covid, dysautonomia, mold, histamine, and more — and lets you ask AI questions like:

- *"What did people with methane SIBO try that actually worked?"*
- *"Compare reported experiences with prucalopride versus low-dose naltrexone."*
- *"Find people who described going from severe to recovered. What did they do?"*
- *"Are there overlapping treatments helping people across SIBO, MCAS, and long covid?"*

The AI runs searches across the database, reads the actual posts and comments, and synthesizes an answer with links back to the original threads.

> **You do not need to know how to code to use this.** If you have Claude Desktop, Claude Code, or ChatGPT's Codex CLI, you can have it running in about 10 minutes.

> **What this isn't:** medical advice. The data is real patients reporting their experience publicly on Reddit. Use it to find patterns and leads to bring to your doctor — not to diagnose or treat yourself.

---

## Install — pick your path

### 🟢 Easiest: you have Claude Code or Codex CLI

**Just ask the AI to install it for you.** Copy one of these prompts and paste it into Claude Code or Codex:

> ```
> Please install the sibo-research-db MCP server for me.
>
> 1. Clone github.com/toczix/sibo-research-db to a sensible folder on my machine
> 2. Download the database file (reddit.db, ~5.4 GB) from
>    huggingface.co/datasets/toczix/sibo-research-db into that folder
> 3. Add the MCP server to my config so it's available next session
> 4. After install, run the stats tool to confirm it works
>
> The repo's README has the setup details you need.
> ```

The AI will read the README, do the file downloads, edit your config, and verify it works. The download is the slow part — go make coffee.

After it finishes, **restart your AI tool** (close and reopen Claude Code or Codex). New tools will appear and you can start asking questions.

### 🟢 Also easy: you have Claude Desktop

Three clicks, no terminal.

1. **Download the database** (5.4 GB, takes a while on slow internet):
   👉 [reddit.db on Hugging Face](https://huggingface.co/datasets/toczix/sibo-research-db/resolve/main/reddit.db)

   *Or the smaller 1.86 GB compressed version, [reddit.db.zst](https://huggingface.co/datasets/toczix/sibo-research-db/resolve/main/reddit.db.zst), if you have zstd installed (decompress with `zstd -d reddit.db.zst`).*

2. **Download the Claude Desktop extension** (~9 KB, instant):
   👉 [Latest release page](https://github.com/toczix/sibo-research-db/releases/latest) — click the file ending in `.mcpb`

3. **Double-click the `.mcpb` file.** Claude Desktop opens with an install dialog. It asks where your `reddit.db` is — click "Browse" and select the file from step 1. Click Install.

4. **Restart Claude Desktop.** New tools appear. Start asking questions.

No editing config files, no command line, no Python knowledge.

### 🟡 Developer: you know what you're doing

If you're comfortable with terminals and config files, [skip to the developer setup](#developer-setup) further down.

---

## What's in the database

Real patient comments from public Reddit subs (not generated, not made up):

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

**18 subreddits. 695,050 posts. 7,205,554 comments.** Range: roughly the start of each subreddit through May 2026.

---

## Examples — what you can ask

Once it's installed, try things like:

**Treatment research**
- *"What did people who responded to LDN have in common?"*
- *"Compare reported rifaximin outcomes for hydrogen versus methane SIBO."*
- *"Show me long-term tolerance reports for prucalopride."*
- *"Has anyone tried [obscure treatment] and what happened?"*

**Pattern finding**
- *"Find users who describe both POIS and SIBO. What do they have in common?"*
- *"Are there overlapping treatments helping people across MCAS, dysautonomia, and long covid?"*
- *"What protocols are getting positive reports in r/SiboSuccessStories?"*

**Sanity checks**
- *"How widely is [supplement] discussed? Is it actually as popular as the marketing makes it sound?"*
- *"Compare mentions of motegrity vs prucalopride vs LDN."*
- *"What are people reporting about [doctor's recommendation] in the data?"*

**Deep dives**
- *"Pull up the top-scored post in r/SIBO about elemental diet and summarize the comment thread."*
- *"Find the most active voices on biofilm protocols and trace their reported journeys."*

The AI runs the searches, reads the actual content, and tells you what it found — with links back to the original Reddit threads so you can verify and read more.

---

## Honest expectations

**This is patient-reported experience, not clinical data.** People misremember, exaggerate, and skip the boring parts. The subs are biased toward people still sick — people who recover usually stop posting.

**What this is great for:**
- Finding patterns across many people that single anecdotes hide
- Generating leads to bring to a doctor or to look up in clinical literature
- Sanity-checking marketing claims against real reported experience
- Tracing one person's journey across their comments

**What this isn't:**
- A diagnostic tool
- A replacement for your doctor or for clinical research
- A success-rate calculator (selection bias is severe)
- A way to identify or contact people from the data

**Please don't:**
- DM users you find in the database (they're real sick people, not advisors)
- Make treatment decisions based on Reddit posts alone
- Republish named user content commercially

If you're a Reddit user whose content is in here and you want it removed from future updates, [open an issue](https://github.com/toczix/sibo-research-db/issues).

---

## If something goes wrong

**The `.mcpb` won't install or Claude Desktop doesn't recognize it.**
Update Claude Desktop. The extension format needs version 0.10 or newer.

**Database download keeps failing or is too slow.**
Try the compressed `.zst` version — it's 1.86 GB instead of 5.4 GB. You'll need `zstd` installed (`brew install zstd` on Mac, your package manager on Linux, [download for Windows](https://github.com/facebook/zstd/releases)).

**The AI says "database not found" or similar.**
The Claude Desktop install dialog asks where your `reddit.db` is. Make sure you pointed it at the actual file, not the folder containing it.

**It works but the first query is slow.**
Normal. SQLite has to warm up its cache. Second query onwards is fast.

**You asked Claude Code or Codex to install it and something broke.**
Tell it what error you saw and ask it to fix it. The README has all the info it needs to debug most things.

**Anything else.**
[Open an issue on GitHub](https://github.com/toczix/sibo-research-db/issues). Include: which AI tool you're using, what you tried, and what you saw.

---

## Optional: layer your personal research notes

If you keep your own research document (symptom timeline, test results, treatment hypotheses), you can expose it to the AI as an extra tool. Set these environment variables in your config:

```
SIBO_REPORT=/path/to/your/research.md
SIBO_SYMPTOMS=/path/to/your/symptoms.md
```

When set, the AI gets two extra tools — `get_report` and `get_symptoms` — that read your local files. Useful for asking *"given my symptom profile and the database, what hasn't been tried yet?"* without pasting your notes every conversation.

Without those env vars, the tools don't exist. Nothing personal gets exposed in the default install.

---

# Developer setup

The sections below assume comfort with a terminal, JSON config, and Python tooling. Skip if you're using one of the easy paths above.

## Prerequisites

- **Python 3.10+** (3.11+ recommended)
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)**:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- **~7 GB free disk** (5.4 GB for the database + working room)

## Quick start

```bash
# Clone the repo
git clone https://github.com/toczix/sibo-research-db.git
cd sibo-research-db

# Get the database
uv tool install huggingface_hub
hf download toczix/sibo-research-db reddit.db --repo-type dataset --local-dir .

# Install deps and smoke test
uv sync
uv run python search.py stats
uv run python search.py search "ginger AND artichoke" --limit 3
```

If the smoke test prints subreddit counts and a few search hits, you're ready to configure your AI tool.

## Setup: Claude Desktop (manual JSON)

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "sibo-research-db": {
      "command": "uv",
      "args": [
        "--directory",
        "/absolute/path/to/sibo-research-db",
        "run",
        "python",
        "server.py"
      ]
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

## Setup: Cline / Continue / other MCP clients

Same shape — `command: "uv"`, args pointing at this directory's `server.py`. The server speaks stdio MCP.

## CLI usage (no AI)

```bash
uv run python search.py stats
uv run python search.py search "rifaximin AND biofilm" --limit 10
uv run python search.py thread 1jyj8vp
uv run python search.py export "POIS" -o pois_results.jsonl
```

## Available tools

10 public tools:

- `stats`, `list_subreddits` — orient yourself
- `search` — FTS5 query with date/sub/score filters
- `get_thread`, `get_post` — pull specific content
- `get_top_posts` — highest-scored discussions
- `count_mentions`, `compare_mentions` — how widely something is discussed
- `find_active_voices` — power users on a topic (with built-in "do not contact" warning)
- `sql_query` — read-only arbitrary SELECT, capped at 200 rows

Tables: `posts(id, subreddit, author, title, selftext, score, num_comments, created_utc, permalink, ...)` and `comments(id, subreddit, author, body, score, created_utc, link_id, parent_id, permalink)`. FTS5 virtual tables for search: `posts_fts(title, selftext)` and `comments_fts(body)`.

## Safety

- SQLite opens in `mode=ro&immutable=1` with `PRAGMA query_only=ON` — writes physically can't happen
- All limit parameters clamped to bounded ranges
- `sql_query` streams via `fetchmany()` and caps at 200 rows
- FTS5 errors caught and returned as readable hints
- `find_active_voices` includes a "do not contact" warning in its response

## Verify the database

```bash
sqlite3 reddit.db "PRAGMA integrity_check;"  # should print "ok"
shasum -a 256 reddit.db                      # compare against checksums.txt on HF
```

## Build it yourself

To regenerate the database from scratch or add more subreddits:

```bash
# Edit download_subreddits.py to change the SUBREDDITS list, then:
python download_subreddits.py                  # download all defaults
python download_subreddits.py NewSubreddit     # add just one

# Ingest into SQLite:
python ingest_all.py
```

Downloads pull from [arctic-shift](https://arctic-shift.photon-reddit.com), a public Reddit archive. Full ingest is roughly a day end-to-end.

## Build the Claude Desktop extension

```bash
./scripts/build-mcpb.sh
```

Produces `sibo-research-db-${VERSION}.mcpb`. Attach to a GitHub release.

---

## License

**Code:** MIT (see [LICENSE](LICENSE)).

**Reddit content** in the database is owned by its original authors and Reddit. It's redistributed here from the public [arctic-shift](https://arctic-shift.photon-reddit.com) archive for research and educational use, similar to how Pushshift was used by researchers for years. This is not a claim of public-domain status.

If you're a Reddit user whose content is included and want it removed from future updates, open an issue.

## Built with

- [SQLite](https://www.sqlite.org/) + [FTS5](https://www.sqlite.org/fts5.html)
- [arctic-shift](https://arctic-shift.photon-reddit.com)
- [MCP](https://modelcontextprotocol.io) + [FastMCP](https://github.com/modelcontextprotocol/python-sdk)
