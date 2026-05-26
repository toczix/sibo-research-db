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

# Sibo Reddit Research Database

**A searchable database of 7 million real patient comments from 18 chronic-illness subreddits.**

Built for people researching SIBO, MCAS, IBS, long COVID, dysautonomia, histamine intolerance, mold illness, and adjacent conditions. Lets you ask AI questions like *"what worked for people with methane SIBO?"* or *"compare reported experiences with prucalopride and LDN"* — and get answers grounded in thousands of real patient reports with links back to the original threads.

You don't need to know how to code to use this. The [setup guide on GitHub](https://github.com/toczix/sibo-research-db) walks you through three install paths, the easiest of which requires zero terminal commands.

> **Not medical advice.** This is patient-reported experience. People misremember, exaggerate, and miss confounders. Use it to spot patterns and generate leads to bring to a doctor — never as a substitute for clinical care.

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

## Setup

Full setup guide is on GitHub: **[github.com/toczix/sibo-research-db](https://github.com/toczix/sibo-research-db)**

The TL;DR for non-coders: if you have Claude Code or ChatGPT's Codex CLI, just ask the AI to install it for you — paste the prompt from the README and walk away. If you have Claude Desktop, download a small `.mcpb` extension file, double-click, and point it at the `reddit.db` from this page. No terminal required.

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

## Honest expectations

This is patient-reported data from public Reddit posts. It has real value and real limits:

**Useful for:**
- Pattern-finding across thousands of accounts that single anecdotes can't show
- Generating hypotheses and leads to bring to clinicians or peer-reviewed literature
- Sanity-checking marketing claims against real reported outcomes
- Tracing one user's reported journey across their comments

**Not useful for:**
- Self-diagnosing
- Self-prescribing
- Computing success rates (selection bias is severe — people who recover usually stop posting)
- Identifying or contacting real people

**Please don't:**
- DM users you find in the data
- Build tools that imitate or republish named user content commercially
- Train models intended to mimic specific Reddit users

If you're a Reddit user whose content is included and you want it removed from future updates, [open an issue on the GitHub repo](https://github.com/toczix/sibo-research-db/issues).

## Licensing

**Code** in the [GitHub repo](https://github.com/toczix/sibo-research-db) is MIT-licensed.

**Reddit content** is owned by its original authors and Reddit. It's being redistributed here from the public [arctic-shift](https://arctic-shift.photon-reddit.com) archive for research and educational use. This is not a claim of public-domain status.

## Source

Scraped from [arctic-shift](https://arctic-shift.photon-reddit.com), a public Reddit archive (no API key needed). The scrape and ingest scripts are in the [GitHub repo](https://github.com/toczix/sibo-research-db) if you want to rebuild from scratch or add other subreddits.
