# sibo-research-db

A searchable database of **7,205,554 comments and 695,050 posts** from 18 health subreddits, exposed as an [MCP](https://modelcontextprotocol.io) server so you can query it conversationally with Claude, ChatGPT (via Codex), Cursor, Cline, or any other MCP-compatible AI tool.

Built originally to research refractory SIBO, but covers a wider net of chronic-illness communities. Useful for finding patient-reported outcomes, treatment patterns, dose ranges, common side effects, and "what people like me actually tried" across many cases.

> **Important:** This is patient-reported experience data. It is **not** medical advice, has **not** been clinically validated, and Reddit users are not vetted experts. Use it to surface patterns and leads worth bringing to a doctor or to clinical literature — not as a substitute for either.

## What's in it

| Subreddit | Comments | Topic |
|---|---:|---|
| r/covidlonghaulers | 1,883,928 | Long COVID |
| r/Supplements | 894,256 | Supplement protocols |
| r/ibs | 892,121 | Irritable bowel syndrome |
| r/SIBO | 710,128 | Small intestinal bacterial overgrowth |
| r/MCAS | 558,683 | Mast cell activation syndrome |
| r/dysautonomia | 433,599 | POTS / autonomic dysfunction |
| r/Microbiome | 313,367 | Gut microbiome general |
| r/LongCovid | 257,465 | Long COVID (separate community) |
| r/Candida | 251,539 | Candida overgrowth |
| r/FODMAPS | 249,222 | Low-FODMAP diet |
| r/HistamineIntolerance | 227,376 | Histamine reactions |
| r/FoodAllergies | 203,735 | Food sensitivities and allergies |
| r/ToxicMoldExposure | 188,293 | Mold illness / CIRS |
| r/GutHealth | 57,892 | Gut health general |
| r/Longcovidgutdysbiosis | 36,437 | LC + gut overlap |
| r/FunctionalMedicine | 28,322 | Functional / integrative medicine |
| r/LeakyGutSyndrome | 11,890 | Intestinal permeability |
| r/SiboSuccessStories | 7,301 | Recovery stories — small but high-signal |

Date range: roughly the start of each sub through May 2026. (r/ibs and r/Supplements are limited to 2021+ to keep the database manageable.)

## Why use it

LLMs are good at synthesizing patient experience but they can't see it unless you give it to them. Instead of pasting one anecdote at a time, this lets you ask things like:

- "What did the people who reported responding to LDN have in common?"
- "Compare reported rifaximin outcomes across hydrogen vs. methane SIBO posts."
- "Find the most upvoted protocols for histamine intolerance that mention DAO enzymes."
- "Show me people who took prucalopride long term and how they described tolerance over time."

The AI runs SQL and full-text-search queries against the database, reads the actual posts and comments, and synthesizes an answer with sources.

## Prerequisites

- **Python 3.10+** (3.11+ recommended)
- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** — fastest way to manage Python deps:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh   # macOS / Linux
  # Or: pip install uv
  ```
- **~7 GB free disk** (5.4 GB for the database + working room)
- A few GB of free RAM for SQLite + the AI tool

Works on macOS, Linux, and Windows.

## Quick start

### 1. Clone this repo

```bash
git clone https://github.com/toczix/sibo-research-db.git
cd sibo-research-db
```

### 2. Get the database

The database file (~5.4 GB) is hosted separately on Hugging Face:

```bash
# Option A: with the hf CLI (recommended — resumable, handles errors)
uv tool install huggingface_hub
hf download toczix/sibo-research-db reddit.db --repo-type dataset --local-dir .

# Option B: direct download
curl -L -o reddit.db https://huggingface.co/datasets/toczix/sibo-research-db/resolve/main/reddit.db
```

### 3. Install dependencies + verify it works (smoke test)

Before touching any AI config, confirm the database and code are happy:

```bash
uv sync
uv run python search.py stats
uv run python search.py search "ginger AND artichoke" --limit 3
```

You should see subreddit counts and a few hits. If those work, the MCP server will work — configuring it is just plumbing.

### 4. Connect it to your AI tool

Pick your tool below.

---

## Setup: Claude Desktop (one-click install)

The easiest path. **Skip the JSON config entirely.**

1. Download the latest **`sibo-research-db-0.2.0.mcpb`** file from the [Releases page](https://github.com/toczix/sibo-research-db/releases/latest).
2. Double-click the file. Claude Desktop opens with an "Install Extension" dialog showing the tools the extension provides.
3. When prompted for the **database file**, point at the `reddit.db` you downloaded from Hugging Face in step 2 of the Quick Start.
4. Click Install. Done.

No editing JSON, no figuring out PATH issues, no manual restarts. Claude Desktop handles `uv` and Python dependencies for you.

If you'd rather configure it by hand (older Claude Desktop, or you prefer config files), edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

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

Replace `/absolute/path/to/sibo-research-db` with where you cloned this repo. Restart Claude Desktop. You should see "sibo-research-db" in the tools menu.

**If Claude Desktop can't find `uv`:** GUI apps don't always inherit your shell PATH. Run `which uv` and use the full path (e.g. `/Users/you/.local/bin/uv`) in the config.

## Setup: Claude Code

Use the built-in `claude mcp add` command rather than editing config by hand:

```bash
claude mcp add --transport stdio --scope user sibo-research-db \
  -- uv --directory /absolute/path/to/sibo-research-db run python server.py
```

Then verify:

```bash
claude mcp list
```

You'll see `sibo-research-db` listed. The next time you start `claude`, the tools are available.

## Setup: OpenAI Codex CLI

```bash
codex mcp add sibo-research-db \
  -- uv --directory /absolute/path/to/sibo-research-db run python server.py
```

Or edit `~/.codex/config.toml` directly:

```toml
[mcp_servers.sibo-research-db]
command = "uv"
args = [
  "--directory",
  "/absolute/path/to/sibo-research-db",
  "run",
  "python",
  "server.py",
]
```

## Setup: Cursor

Cursor reads `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (per-project):

```json
{
  "mcpServers": {
    "sibo-research-db": {
      "type": "stdio",
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

## Setup: VS Code (GitHub Copilot Agent)

Add `.vscode/mcp.json` to your workspace (or `~/.config/Code/User/mcp.json` globally):

```json
{
  "servers": {
    "sibo-research-db": {
      "type": "stdio",
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

Then enable MCP in Copilot Agent settings.

## Setup: Cline

Use Cline's MCP panel (UI), or edit `~/Library/Application Support/Code/User/globalStorage/saoudrizwan.claude-dev/settings/cline_mcp_settings.json`:

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

## Setup: Continue / other MCP clients

Same pattern. Whatever the client's MCP config format is, point the `command` at `uv` and the `args` at `server.py` in this directory. The server speaks stdio MCP, no special transport needed.

## No AI: use the CLI directly

If you just want to grep the dataset by hand, `search.py` is a standalone tool — no MCP, no AI:

```bash
uv run python search.py stats
uv run python search.py search "rifaximin AND biofilm" --limit 10
uv run python search.py thread 1jyj8vp
uv run python search.py export "POIS" -o pois_results.jsonl
```

## What the AI can do with it

Once connected, the AI has these tools available:

- **`stats`** — total counts, sub breakdown, date range. Good first call to orient.
- **`list_subreddits`** — every sub in the dataset with counts.
- **`search(query, ...)`** — full-text search across posts and comments. Supports `AND`, `OR`, `NOT`, `NEAR()`, quoted phrases, date range, score filter, sub filter.
- **`get_thread(post_id)`** — pull a whole thread (OP + top comments) for deep analysis.
- **`get_post(post_id)`** — single post without comments.
- **`get_top_posts(subreddit, ...)`** — highest-scored posts in a sub.
- **`count_mentions(term)`** — how many posts/comments mention something, with subreddit breakdown.
- **`compare_mentions([term1, term2, ...])`** — side-by-side comparison of how widely different things are discussed.
- **`find_active_voices(query)`** — users with the most reported experience on a topic. **Output is for tracing one person's perspective across their comments — not for contacting them.**
- **`sql_query(query)`** — for power users: arbitrary read-only SELECT against `posts` and `comments` tables. Capped at 200 rows. Connection is read-only at the SQLite level.

Tables: `posts(id, subreddit, author, title, selftext, score, num_comments, created_utc, permalink, link_flair_text, domain, is_self)` and `comments(id, subreddit, author, body, score, created_utc, link_id, parent_id, permalink)`. FTS5 virtual tables `posts_fts(title, selftext)` and `comments_fts(body)`.

## Example questions to ask

- "What treatments for methane SIBO get the most positive reported outcomes in the dataset?"
- "Find the failure patterns for people who did multiple rounds of rifaximin."
- "Are there overlapping things that help POIS, SIBO, and MCAS that get mentioned in all three subs?"
- "Compare reported LDN dose protocols across the autoimmune subs."
- "Show me threads where someone described going from severe to recovered and what they reported doing."
- "How widely is prucalopride discussed compared to motegrity? Are they used interchangeably?"

## A note on data quality

This is real patient-reported experience. It's not medical advice and it's not clinically validated. People misremember, exaggerate, miss confounders, sometimes flat-out lie, and the subs are heavily selection-biased (people who are doing well usually don't post). The dataset is best used as a way to:

1. **Find leads** worth bringing to a doctor or to clinical literature.
2. **Spot patterns** across many people that single anecdotes hide.
3. **Sanity-check** whether something you've been told is working for others — or whether the failure rate is being undersold.

It's not a replacement for clinical research, your doctor, or your own judgement. Use the language of *reported outcomes* and *patient experience*, not *success rates*.

### A note on the people in the data

The dataset preserves Reddit usernames because that's what makes `find_active_voices` and thread reconstruction work. But these are real people — many of them sick, many of them sharing things they wouldn't share publicly if they thought every word would be indexed and AI-readable.

**Please don't use this data to:**
- DM or contact users you found through the database
- Build anything that re-publishes named user content commercially
- Train models that imitate or impersonate specific users

If you're a Reddit user in the data and want your content removed from future rebuilds, open an issue on this repo with your username.

## Build it yourself (fresher data, or different subs)

The Hugging Face dump is a snapshot. To rebuild from scratch or add subreddits:

```bash
# Edit download_subreddits.py to change the SUBREDDITS list, then:
python download_subreddits.py                  # download all defaults
python download_subreddits.py NewSubreddit     # add just one

# Ingest the JSONL files into the database:
python ingest_all.py                           # ingests everything in ~/Downloads
```

Downloads pull from [arctic-shift](https://arctic-shift.photon-reddit.com), a public Reddit archive (no API key needed). Full ingest takes about a day end-to-end depending on sub size.

## Verify the database

After downloading:

```bash
sqlite3 reddit.db "PRAGMA integrity_check;"   # should print "ok"
sqlite3 reddit.db "SELECT COUNT(*) FROM posts; SELECT COUNT(*) FROM comments;"
```

SHA256 checksums for each release are listed on the [Hugging Face dataset page](https://huggingface.co/datasets/toczix/sibo-research-db).

## Licensing

**Code** in this repository: MIT.

**Reddit content** in the database is owned by its original authors and Reddit. It's being redistributed here from the public [arctic-shift](https://arctic-shift.photon-reddit.com) archive for research and educational use, similar in spirit to how Pushshift was used by researchers for years. This is not a claim of public-domain status. If you're an author whose content is included and you want it removed from future rebuilds, open an issue.

Don't use this dataset for commercial republication of named user content, or for anything that would harm the people who wrote the posts.

## Built with

- [SQLite](https://www.sqlite.org/) + [FTS5](https://www.sqlite.org/fts5.html) for the database and full-text search
- [arctic-shift](https://arctic-shift.photon-reddit.com) for the Reddit archive
- [MCP](https://modelcontextprotocol.io) for the AI tool layer
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) for the Python server
