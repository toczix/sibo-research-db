# sibo-research-db

A searchable database of **7,198,253 comments and 694,390 posts** from 17 health subreddits, exposed as an [MCP](https://modelcontextprotocol.io) server so you can query it conversationally with Claude, ChatGPT (via Codex), Cursor, or any other MCP-compatible AI tool.

Built originally to research refractory SIBO, but covers a wider net of chronic-illness communities. Useful for finding patient-reported outcomes, treatment patterns, dose ranges, common side effects, and "what actually worked for people like me" across thousands of real cases.

## What's in it

| Subreddit | Comments | Topic |
|---|---:|---|
| r/covidlonghaulers | 1,883,928 | Long COVID |
| r/Supplements | 894,256 | Supplement protocols |
| r/ibs | 892,121 | Irritable bowel syndrome |
| r/SIBO | 710,128 | Small intestinal bacterial overgrowth |
| r/MCAS | 558,683 | Mast cell activation syndrome |
| r/dysautonomia | 433,599 | POTS and autonomic dysfunction |
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

Date range: roughly the start of each sub through May 2026. (r/ibs and r/Supplements are limited to 2021+ to keep the database manageable.)

## Why use it

LLMs are pretty good at synthesizing patient experience data but they can't see it unless you give it to them. Instead of pasting one anecdote at a time, this lets you ask things like:

- "What did the people who responded well to LDN have in common?"
- "Compare rifaximin success rates across hydrogen vs. methane SIBO posts."
- "Find the most upvoted protocols for histamine intolerance that mention DAO enzymes."
- "Show me everyone who took prucalopride long term and whether they developed tolerance."

The AI runs SQL and full-text-search queries against the database, reads the actual posts and comments, and synthesizes an answer with sources.

## Quick start (5 minutes)

### 1. Clone this repo

```bash
git clone https://github.com/toczix/sibo-research-db.git
cd sibo-research-db
```

### 2. Get the database

The database file (~5.4GB) is hosted separately on Hugging Face:

```bash
# Option A: with the hf CLI (recommended)
pip install huggingface_hub      # or: uv tool install huggingface_hub
hf download toczix/sibo-research-db reddit.db --repo-type dataset --local-dir .

# Option B: direct download
curl -L -o reddit.db https://huggingface.co/datasets/toczix/sibo-research-db/resolve/main/reddit.db
```

### 3. Install dependencies

```bash
# With uv (fastest, recommended)
uv sync

# Or with pip
pip install "mcp[cli]>=1.27.1"
```

### 4. Connect it to your AI tool

Pick your tool below.

---

## Setup: Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "sibo-research-db": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/sibo-research-db",
        "python",
        "server.py"
      ]
    }
  }
}
```

Replace `/absolute/path/to/sibo-research-db` with where you cloned this repo. Restart Claude Desktop. You should see "sibo-research-db" in the tools menu.

## Setup: Claude Code

Add to your project's `.claude/settings.json` (or your global `~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "sibo-research-db": {
      "command": "uv",
      "args": [
        "run",
        "--directory",
        "/absolute/path/to/sibo-research-db",
        "python",
        "server.py"
      ]
    }
  }
}
```

## Setup: OpenAI Codex CLI

Codex CLI (the new OpenAI terminal agent) supports MCP servers via `~/.codex/config.toml`:

```toml
[mcp_servers.sibo-research-db]
command = "uv"
args = [
  "run",
  "--directory",
  "/absolute/path/to/sibo-research-db",
  "python",
  "server.py",
]
```

Then start `codex` and the tools will be available.

## Setup: Cursor

Cursor supports MCP via Settings → Features → Model Context Protocol. Add:

```json
{
  "mcpServers": {
    "sibo-research-db": {
      "command": "uv",
      "args": ["run", "--directory", "/absolute/path/to/sibo-research-db", "python", "server.py"]
    }
  }
}
```

## Setup: Cline / Continue / other MCP clients

Same pattern. Whatever the client's MCP config format is, point the `command` at `uv` (or `python`) and the `args` at `server.py` in this directory.

## No AI: use the CLI directly

If you just want to grep the dataset by hand, `search.py` is a standalone tool:

```bash
python search.py stats
python search.py search "rifaximin AND biofilm" --limit 10
python search.py thread 1jyj8vp
python search.py export "POIS" -o pois_results.jsonl
```

## What the AI can do with it

Once connected, the AI has these tools:

- **`search(query, ...)`** — full-text search across posts and comments. Supports `AND`, `OR`, `NOT`, `NEAR()`, and quoted phrases.
- **`get_thread(post_id)`** — pull a whole thread (OP + top comments) for deep analysis.
- **`get_top_posts(subreddit, ...)`** — highest-scored posts in a sub.
- **`count_mentions(term)`** — how many times something is discussed across the dataset, broken down by sub.
- **`find_users(query)`** — find power users on a topic (the experts and the lived-experience folks).
- **`stats()`** — total counts, sub breakdowns, date range.
- **`sql_query(query)`** — for power users, run any read-only SELECT against the raw tables.

Tables: `posts(id, subreddit, author, title, selftext, score, num_comments, created_utc, permalink)` and `comments(id, subreddit, author, body, score, created_utc, link_id, parent_id, permalink)`. FTS5 virtual tables `posts_fts` and `comments_fts` for search.

## Example questions to ask

- "What treatments for methane SIBO get the highest praise in the dataset?"
- "Find the failure patterns for people who did multiple rounds of rifaximin."
- "Are there any patterns in what helps POIS that overlap with SIBO/MCAS communities?"
- "Compare LDN dose protocols across the autoimmune subs."
- "Show me threads where someone went from severe to recovered and what they did."

## Build it yourself (if you want fresh data, or different subs)

The Hugging Face dump is a snapshot. If you want fresher data or to add subreddits:

```bash
# Edit download_subreddits.py to change the SUBREDDITS list
python download_subreddits.py                       # download all defaults
python download_subreddits.py NewSubreddit          # add just one

# Ingest the JSONL files into the database
python ingest_all.py                                # ingests everything in ~/Downloads
```

Downloads pull from [arctic-shift](https://arctic-shift.photon-reddit.com), a public Reddit archive (no API key needed). Full ingest takes about a day end-to-end depending on sub size.

## A note on the data

This is real patient-reported experience. It's not medical advice and it's not clinically validated. People misremember, exaggerate, miss confounders, and sometimes flat-out lie. The dataset is best used as a way to:

1. **Find leads** worth bringing to a doctor or doing your own research on.
2. **Spot patterns** across many people that single anecdotes hide.
3. **Sanity-check** whether something you've been told is actually working for others, or whether the failure rate is being undersold.

It's not a replacement for clinical literature or a doctor. It's a way to systematically read the patient-reported side of things, which medicine often ignores.

## License

MIT. The Reddit data itself is public domain content scraped from a public archive.

## Built with

- [SQLite](https://www.sqlite.org/) + [FTS5](https://www.sqlite.org/fts5.html) for the database and full-text search
- [arctic-shift](https://arctic-shift.photon-reddit.com) for the Reddit archive
- [MCP](https://modelcontextprotocol.io) for the AI tool layer
- [FastMCP](https://github.com/modelcontextprotocol/python-sdk) for the Python server
