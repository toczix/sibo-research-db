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

A searchable SQLite database of **7,198,253 comments and 694,390 posts** from 17 health-focused subreddits, scraped from the public [arctic-shift](https://arctic-shift.photon-reddit.com) archive.

Designed to be queried by AI tools (Claude, ChatGPT/Codex, Cursor, Cline, etc.) via the [sibo-research-db MCP server](https://github.com/toczix/sibo-research-db), but works as a standalone SQLite + FTS5 database for any kind of analysis.

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

Full-text search via FTS5 virtual tables: `posts_fts` (title + selftext) and `comments_fts` (body).

## Download

```bash
# With the Hugging Face CLI
hf download toczix/sibo-research-db reddit.db --repo-type dataset --local-dir .

# Or directly
curl -L -o reddit.db https://huggingface.co/datasets/toczix/sibo-research-db/resolve/main/reddit.db
```

File is ~5.4 GB.

## Use with AI tools

See https://github.com/toczix/sibo-research-db for the MCP server and setup instructions for Claude Desktop, Claude Code, Codex CLI, Cursor, and Cline.

## Use with plain SQL

```python
import sqlite3
conn = sqlite3.connect("reddit.db")
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

## License

MIT (for the database structure and tooling). The Reddit content itself is owned by its respective authors and is being made available here for research and education under fair use, mirroring the structure of public archives like arctic-shift and Pushshift.

If you're an author and want your content removed, open an issue on the GitHub repo and I'll add a removal pass to the next rebuild.

## Disclaimer

This is patient-reported experience data. **It is not medical advice and has not been clinically validated.** People misremember, exaggerate, and miss confounders. Use this dataset to find patterns and leads worth bringing to a doctor or to clinical literature — not as a substitute for either.
