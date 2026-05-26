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

<p align="center">
  <img src="banner.png" alt="Sibo Research Database — Chat with 7 million real patient experiences from 18 health subreddits" width="100%" />
</p>

# Sibo Reddit Research Database

### Chat with 7 million real patient experiences from 18 health subreddits — find what's actually working for symptoms like yours.

A SQLite database of public Reddit content from chronic-illness communities, designed to be queried conversationally by AI tools (Claude Desktop, Claude Code, Codex CLI, Cursor, Cline, VS Code Copilot Agent).

> **Not medical advice.** Patient-reported data, not clinical. Use to find patterns and leads worth bringing to a doctor — never to diagnose or treat yourself.

## Install in 3 steps

**Step 1.** Copy this into Claude Code or Codex CLI:

```
https://github.com/toczix/sibo-research-db
https://huggingface.co/datasets/toczix/sibo-research-db

I want to chat with this database for my SIBO-related symptoms. Please
install it for me — follow the README in the GitHub repo.
```

**Step 2.** Wait for the install (downloads a 5.4 GB database — go make coffee).

**Step 3.** Restart your AI tool. Start asking questions.

Full setup guide and Claude Desktop one-click install at **[github.com/toczix/sibo-research-db](https://github.com/toczix/sibo-research-db)**.

## Files

| File | Size | What it is |
|---|---:|---|
| **`reddit.db`** | 5.4 GB | The database. SQLite with full-text-search indexes. Ready to use as-is. |
| **`reddit.db.zst`** | 1.86 GB | Same database, compressed 66% smaller. Decompress with `zstd -d reddit.db.zst`. |
| `checksums.txt` | 530 B | SHA-256 for both files |

**You only need ONE of `reddit.db` or `reddit.db.zst`.** Pick the compressed one for faster download (you'll need [zstd](https://github.com/facebook/zstd) installed, which is one command on Mac/Linux/Windows).

## What's in it

| Subreddit | Topic | Comments |
|---|---|---:|
| r/covidlonghaulers | Long COVID | 1,883,928 |
| r/Supplements | Supplement protocols | 894,256 |
| r/ibs | IBS | 892,121 |
| r/SIBO | SIBO | 710,128 |
| r/MCAS | Mast cell activation | 558,683 |
| r/dysautonomia | POTS / autonomic | 433,599 |
| r/Microbiome | Gut microbiome | 313,367 |
| r/LongCovid | Long COVID (alt community) | 257,465 |
| r/Candida | Candida overgrowth | 251,539 |
| r/FODMAPS | Low-FODMAP diet | 249,222 |
| r/HistamineIntolerance | Histamine reactions | 227,376 |
| r/FoodAllergies | Food sensitivities | 203,735 |
| r/ToxicMoldExposure | Mold illness | 188,293 |
| r/GutHealth | Gut health general | 57,892 |
| r/Longcovidgutdysbiosis | LC + gut overlap | 36,437 |
| r/FunctionalMedicine | Functional medicine | 28,322 |
| r/LeakyGutSyndrome | Intestinal permeability | 11,890 |
| r/SiboSuccessStories | Recovery stories | 7,301 |

**18 subreddits. 695,050 posts. 7,205,554 comments.** Coverage roughly the start of each sub through May 2026 (r/ibs and r/Supplements are limited to 2021+ to keep the database manageable).

## Using it without AI

The database is a regular SQLite file. You can query it directly:

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

Schema:

```sql
posts(id, subreddit, author, title, selftext, score, num_comments,
      created_utc, permalink, link_flair_text, domain, is_self)

comments(id, subreddit, author, body, score, created_utc,
         link_id, parent_id, permalink)
```

Full-text search via FTS5 virtual tables `posts_fts(title, selftext)` and `comments_fts(body)`.

## Verify your download

```bash
sqlite3 reddit.db "PRAGMA integrity_check;"   # should print "ok"
sqlite3 reddit.db "SELECT COUNT(*) FROM posts; SELECT COUNT(*) FROM comments;"
shasum -a 256 reddit.db                       # compare against checksums.txt
```

## Licensing

**Code** in the [GitHub repo](https://github.com/toczix/sibo-research-db) is MIT-licensed.

**Reddit content** is owned by its original authors and Reddit. It's being redistributed here from the public [arctic-shift](https://arctic-shift.photon-reddit.com) archive for research and educational use. This is not a claim of public-domain status.

## Source

Scraped from [arctic-shift](https://arctic-shift.photon-reddit.com), a public Reddit archive (no API key needed). The scrape and ingest scripts are in the [GitHub repo](https://github.com/toczix/sibo-research-db) if you want to rebuild from scratch or add other subreddits.
