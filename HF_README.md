---
license: mit
task_categories:
  - text-retrieval
  - question-answering
language:
  - en
tags:
  - reddit
  - health
  - sibo
  - mcas
  - ibs
  - long-covid
  - microbiome
  - patient-reported-outcomes
pretty_name: SIBO Research DB
size_categories:
  - 1M<n<10M
---

# sibo-research-db

A searchable SQLite database of **7,205,554 comments and 695,050 posts** from 18 health-focused subreddits, scraped from the public [arctic-shift](https://arctic-shift.photon-reddit.com) Reddit archive.

Designed to be queried by AI tools (Claude, ChatGPT/Codex, Cursor, Cline, VS Code Copilot) via the [sibo-research-db MCP server](https://github.com/toczix/sibo-research-db), but works as a standalone SQLite + FTS5 database for any kind of analysis.

> **Important:** This is patient-reported experience data. It is **not** medical advice and has **not** been clinically validated. People misremember, exaggerate, and miss confounders. Use this to find patterns and leads worth bringing to a doctor or clinical literature — not as a substitute for either.

## What's in it

| Subreddit | Comments | Topic |
|---|---:|---|
| r/covidlonghaulers | 1,883,928 | Long COVID |
| r/Supplements | 894,256 | Supplement protocols |
| r/ibs | 892,121 | Irritable bowel syndrome |
| r/SIBO | 710,128 | Small intestinal bacterial overgrowth |
| r/MCAS | 558,683 | Mast cell activation syndrome |
| r/dysautonomia | 433,599 | POTS / autonomic dysfunction |
| r/Microbiome | 313,367 | Gut microbiome |
| r/LongCovid | 257,465 | Long COVID (separate community) |
| r/Candida | 251,539 | Candida overgrowth |
| r/FODMAPS | 249,222 | Low-FODMAP diet |
| r/HistamineIntolerance | 227,376 | Histamine reactions |
| r/FoodAllergies | 203,735 | Food sensitivities |
| r/ToxicMoldExposure | 188,293 | Mold illness / CIRS |
| r/GutHealth | 57,892 | Gut health general |
| r/Longcovidgutdysbiosis | 36,437 | LC + gut overlap |
| r/FunctionalMedicine | 28,322 | Functional / integrative medicine |
| r/LeakyGutSyndrome | 11,890 | Intestinal permeability |
| r/SiboSuccessStories | 7,301 | Recovery stories — small but high-signal |

## Schema

```sql
posts (
  id, subreddit, author, title, selftext,
  score, num_comments, created_utc, permalink,
  link_flair_text, domain, is_self
)

comments (
  id, subreddit, author, body, score,
  created_utc, link_id, parent_id, permalink
)
```

Full-text search via FTS5 virtual tables: `posts_fts(title, selftext)` and `comments_fts(body)`.

## Download

```bash
# With the Hugging Face CLI
hf download toczix/sibo-research-db reddit.db --repo-type dataset --local-dir .

# Or direct
curl -L -o reddit.db https://huggingface.co/datasets/toczix/sibo-research-db/resolve/main/reddit.db
```

Files:

| File | Size | Notes |
|---|---:|---|
| `reddit.db` | ~5.4 GB | The full database, ready to query |
| `reddit.db.zst` | ~2-3 GB | Same DB, zstd-compressed for faster download. Decompress with `zstd -d reddit.db.zst` |
| `checksums.txt` | small | SHA256 of each release artifact |

## Verify after download

```bash
sqlite3 reddit.db "PRAGMA integrity_check;"   # should print "ok"
sqlite3 reddit.db "SELECT COUNT(*) FROM posts; SELECT COUNT(*) FROM comments;"
shasum -a 256 reddit.db                       # compare against checksums.txt
```

## Use with AI tools

See [github.com/toczix/sibo-research-db](https://github.com/toczix/sibo-research-db) for the MCP server and setup instructions for Claude Desktop, Claude Code, Codex CLI, Cursor, Cline, and VS Code Copilot Agent.

## Use with plain SQL

```python
import sqlite3
conn = sqlite3.connect("file:reddit.db?mode=ro", uri=True)
cur = conn.execute("""
    SELECT c.subreddit, c.body, c.score
    FROM comments_fts fts
    JOIN comments c ON c.rowid = fts.rowid
    WHERE comments_fts MATCH 'prucalopride AND tolerance'
    ORDER BY c.score DESC
    LIMIT 10
""")
for row in cur:
    print(row)
```

## Licensing

**Code** in the [GitHub repo](https://github.com/toczix/sibo-research-db) is MIT-licensed.

**Reddit content** in the database is owned by its original authors and Reddit. It's being redistributed here from the public arctic-shift archive for research and educational use, similar to how Pushshift was used by researchers for years. This is **not** a claim of public-domain status.

If you are a Reddit user whose content is included and you want it removed from future rebuilds, open an issue on the GitHub repo with your username and the affected content will be filtered out of the next snapshot.

## Intended use

- Patient/researcher exploratory analysis of self-reported chronic-illness experiences
- Pattern-finding across thousands of accounts that single anecdotes hide
- Generating hypotheses and leads to bring to clinicians or to peer-reviewed literature
- Sanity-checking marketing claims and protocol recommendations against real reported outcomes

## Prohibited use

- Contacting, messaging, or harassing Reddit users found in the data
- Building tools that imitate, impersonate, or republish named user content commercially
- Training models intended to mimic specific users
- Diagnosing, prescribing, or recommending medical treatment based on this data alone

## Disclaimer

This is patient-reported experience data. It has not been clinically validated. People misremember, exaggerate, and miss confounders. The subs are heavily selection-biased — people who recover usually stop posting. Use this dataset to find patterns and leads worth bringing to a doctor or to clinical literature, not as a substitute for either.
