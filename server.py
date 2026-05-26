#!/usr/bin/env python3
"""
sibo-research-db MCP Server

A searchable database of ~7 million comments and ~670k posts from 17 health
subreddits (SIBO, IBS, MCAS, dysautonomia, long covid, microbiome, etc.) for
conversational access via MCP-compatible AI tools (Claude Desktop, Claude Code,
Codex CLI, Cursor, Cline, etc.)

The database is a SQLite file with FTS5 full-text-search indexes on post titles,
post bodies, and comment bodies.
"""

import os
import sqlite3
from datetime import datetime, timezone
from mcp.server.fastmcp import FastMCP

# --- Config ---
# DB lives next to this file by default. Override with SIBO_DB env var.
_HERE = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.environ.get(
    "SIBO_DB",
    os.path.join(_HERE, "reddit.db"),
)

mcp = FastMCP(
    "sibo-research-db",
    instructions="""You have access to a research database of ~670k posts and ~7M comments
from 17 health subreddits (SIBO, MCAS, ibs, Microbiome, covidlonghaulers,
dysautonomia, Supplements, HistamineIntolerance, Candida, FODMAPS,
FoodAllergies, LongCovid, GutHealth, FunctionalMedicine,
Longcovidgutdysbiosis, LeakyGutSyndrome, ToxicMoldExposure).

Use the search tools to find real patient experiences, treatment outcomes, and
clinical discussions. FTS5 queries support AND, OR, NOT, NEAR(), and phrase matching.

Start with `stats` to see what's in the database, then use `search` to dig in.
For analyzing a single thread in depth, use `get_thread`. For gauging how widely
discussed a topic is, use `count_mentions`. For finding power users, use `find_users`.
For custom analytics across the data, use `sql_query`.""",
)


def _connect() -> sqlite3.Connection:
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}.\n"
            f"Download it from https://huggingface.co/datasets/toczix/sibo-research-db "
            f"or build it yourself with the included download_subreddits.py + ingest.py scripts.\n"
            f"Set the SIBO_DB env var to point at a different location."
        )
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _ts_to_date(ts) -> str:
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d")
    except (ValueError, TypeError, OSError):
        return "unknown"


def _format_post(row, include_body: bool = True) -> str:
    date = _ts_to_date(row["created_utc"])
    lines = [
        f"[{row['score']:+d} | {row['num_comments']} comments | {date}] r/{row['subreddit']}",
        f"  {row['title']}",
        f"  ID: {row['id']}",
        f"  https://reddit.com{row['permalink']}",
    ]
    if include_body and row["selftext"]:
        body = row["selftext"][:800]
        if len(row["selftext"]) > 800:
            body += "..."
        lines.append(f"\n  {body}")
    return "\n".join(lines)


def _format_comment(row, max_body: int = 600) -> str:
    date = _ts_to_date(row["created_utc"])
    body = row["body"][:max_body]
    if len(row["body"]) > max_body:
        body += "..."
    lines = [
        f"[{row['score']:+d} | {date}] u/{row['author']} in r/{row['subreddit']}",
        f"  {body}",
    ]
    if row["permalink"]:
        lines.append(f"  https://reddit.com{row['permalink']}")
    return "\n".join(lines)


# ── Tools ────────────────────────────────────────────────────────────────────


@mcp.tool()
def search(
    query: str,
    limit: int = 20,
    min_score: int = 0,
    subreddit: str | None = None,
    search_type: str = "both",
) -> str:
    """Search posts and comments using FTS5 full-text search.

    Args:
        query: FTS5 query. Supports AND, OR, NOT, NEAR(), phrases in quotes.
               Examples: "rifaximin AND biofilm", "POIS NEAR/5 gut", '"wired but tired"'
        limit: Max results per category (posts and comments). Default 20.
        min_score: Minimum upvote score to filter by. Default 0.
        subreddit: Filter to a specific subreddit (without r/ prefix). Optional.
        search_type: "posts", "comments", or "both" (default).
    """
    conn = _connect()
    parts = []

    if search_type in ("both", "posts"):
        where_extra = ""
        params = [query]
        if min_score > 0:
            where_extra += " AND p.score >= ?"
            params.append(min_score)
        if subreddit:
            where_extra += " AND p.subreddit = ?"
            params.append(subreddit)
        params.append(limit)

        sql = f"""
        SELECT p.id, p.subreddit, p.title, p.selftext, p.score, p.num_comments,
               p.created_utc, p.permalink
        FROM posts_fts fts
        JOIN posts p ON p.rowid = fts.rowid
        WHERE posts_fts MATCH ?
        {where_extra}
        ORDER BY rank
        LIMIT ?
        """
        posts = conn.execute(sql, params).fetchall()
        if posts:
            parts.append(f"=== POSTS ({len(posts)} results) ===\n")
            for row in posts:
                parts.append(_format_post(row))
                parts.append("")
        else:
            parts.append("=== POSTS: No results ===\n")

    if search_type in ("both", "comments"):
        where_extra = ""
        params = [query]
        if min_score > 0:
            where_extra += " AND c.score >= ?"
            params.append(min_score)
        if subreddit:
            where_extra += " AND c.subreddit = ?"
            params.append(subreddit)
        params.append(limit)

        sql = f"""
        SELECT c.id, c.subreddit, c.author, c.body, c.score,
               c.created_utc, c.link_id, c.parent_id, c.permalink
        FROM comments_fts fts
        JOIN comments c ON c.rowid = fts.rowid
        WHERE comments_fts MATCH ?
        {where_extra}
        ORDER BY rank
        LIMIT ?
        """
        comments = conn.execute(sql, params).fetchall()
        if comments:
            parts.append(f"\n=== COMMENTS ({len(comments)} results) ===\n")
            for row in comments:
                parts.append(_format_comment(row))
                parts.append("")
        else:
            parts.append("\n=== COMMENTS: No results ===\n")

    conn.close()
    return "\n".join(parts) if parts else "No results found."


@mcp.tool()
def get_thread(post_id: str, comment_limit: int = 50) -> str:
    """Get a full Reddit thread (post + all comments) by post ID.

    Args:
        post_id: The Reddit post ID (e.g. '1jyj8vp', '10hgicq').
                 Works with or without the 't3_' prefix.
        comment_limit: Max comments to return, sorted by score. Default 50.
    """
    conn = _connect()
    post_id_clean = post_id.replace("t3_", "")

    post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id_clean,)).fetchone()
    if not post:
        conn.close()
        return f"Post '{post_id}' not found in database."

    comments = conn.execute(
        "SELECT * FROM comments WHERE link_id = ? OR link_id = ? ORDER BY score DESC LIMIT ?",
        (f"t3_{post_id_clean}", post_id_clean, comment_limit)
    ).fetchall()

    parts = [_format_post(post)]
    if post["selftext"]:
        parts.append(f"\n--- Full post body ---\n{post['selftext']}\n")

    parts.append(f"\n--- {len(comments)} comments (sorted by score) ---\n")
    for c in comments:
        parts.append(_format_comment(c, max_body=1200))
        parts.append("")

    conn.close()
    return "\n".join(parts)


@mcp.tool()
def get_top_posts(
    subreddit: str | None = None,
    limit: int = 25,
    min_comments: int = 5,
) -> str:
    """Get the highest-scored posts, optionally filtered by subreddit.

    Args:
        subreddit: Filter to a specific subreddit (without r/ prefix). Optional.
        limit: Number of posts to return. Default 25.
        min_comments: Minimum number of comments. Default 5.
    """
    conn = _connect()
    where = "WHERE num_comments >= ?"
    params = [min_comments]
    if subreddit:
        where += " AND subreddit = ?"
        params.append(subreddit)
    params.append(limit)

    rows = conn.execute(
        f"SELECT * FROM posts {where} ORDER BY score DESC LIMIT ?", params
    ).fetchall()

    parts = []
    for row in rows:
        parts.append(_format_post(row, include_body=False))
        parts.append("")

    conn.close()
    return "\n".join(parts) if parts else "No posts found."


@mcp.tool()
def count_mentions(term: str, subreddit: str | None = None) -> str:
    """Count how many posts and comments mention a term. Useful for gauging how
    popular or discussed a treatment/supplement/symptom is across the dataset.

    Args:
        term: The term to count (uses FTS5 MATCH, supports AND/OR/phrases).
        subreddit: Optional subreddit filter.
    """
    conn = _connect()

    sub_filter_p = " AND p.subreddit = ?" if subreddit else ""
    sub_filter_c = " AND c.subreddit = ?" if subreddit else ""

    params_p = [term] + ([subreddit] if subreddit else [])
    params_c = [term] + ([subreddit] if subreddit else [])

    post_count = conn.execute(
        f"""SELECT COUNT(*) as cnt FROM posts_fts fts
        JOIN posts p ON p.rowid = fts.rowid
        WHERE posts_fts MATCH ?{sub_filter_p}""", params_p
    ).fetchone()["cnt"]

    comment_count = conn.execute(
        f"""SELECT COUNT(*) as cnt FROM comments_fts fts
        JOIN comments c ON c.rowid = fts.rowid
        WHERE comments_fts MATCH ?{sub_filter_c}""", params_c
    ).fetchone()["cnt"]

    # Get subreddit breakdown if no filter
    breakdown = ""
    if not subreddit:
        sub_counts = conn.execute(
            """SELECT c.subreddit, COUNT(*) as cnt
            FROM comments_fts fts JOIN comments c ON c.rowid = fts.rowid
            WHERE comments_fts MATCH ?
            GROUP BY c.subreddit ORDER BY cnt DESC LIMIT 10""", (term,)
        ).fetchall()
        if sub_counts:
            breakdown = "\n\nSubreddit breakdown (comments):\n"
            for row in sub_counts:
                breakdown += f"  r/{row['subreddit']}: {row['cnt']:,}\n"

    conn.close()
    return f'"{term}" appears in:\n  {post_count:,} posts\n  {comment_count:,} comments\n  {post_count + comment_count:,} total{breakdown}'


@mcp.tool()
def find_users(query: str, min_posts: int = 2, limit: int = 20) -> str:
    """Find the most active/knowledgeable users who discuss a topic.
    Useful for finding experts or people with lived experience.

    Args:
        query: FTS5 search query for the topic.
        min_posts: Minimum number of matching comments from a user. Default 2.
        limit: Max users to return. Default 20.
    """
    conn = _connect()

    rows = conn.execute(
        """SELECT c.author, COUNT(*) as cnt, SUM(c.score) as total_score,
                  GROUP_CONCAT(DISTINCT c.subreddit) as subs
           FROM comments_fts fts
           JOIN comments c ON c.rowid = fts.rowid
           WHERE comments_fts MATCH ? AND c.author != '[deleted]' AND c.author != 'AutoModerator'
           GROUP BY c.author
           HAVING cnt >= ?
           ORDER BY total_score DESC
           LIMIT ?""",
        (query, min_posts, limit)
    ).fetchall()

    parts = [f"Top users discussing '{query}':\n"]
    for row in rows:
        parts.append(
            f"  u/{row['author']} — {row['cnt']} comments, {row['total_score']:+d} total karma"
            f"\n    Active in: {row['subs']}"
        )

    conn.close()
    return "\n".join(parts) if len(parts) > 1 else f"No users found with {min_posts}+ comments matching '{query}'."


@mcp.tool()
def stats() -> str:
    """Get database statistics: total posts/comments, subreddit breakdown, date range."""
    conn = _connect()

    post_count = conn.execute("SELECT COUNT(*) as cnt FROM posts").fetchone()["cnt"]
    comment_count = conn.execute("SELECT COUNT(*) as cnt FROM comments").fetchone()["cnt"]

    parts = [
        f"Database: {DB_PATH}",
        f"Total posts: {post_count:,}",
        f"Total comments: {comment_count:,}",
        "",
        "Subreddit breakdown:",
    ]

    for row in conn.execute(
        """SELECT p.subreddit, COUNT(DISTINCT p.id) as posts,
           (SELECT COUNT(*) FROM comments c WHERE c.subreddit = p.subreddit) as comments
           FROM posts p GROUP BY p.subreddit ORDER BY comments DESC"""
    ):
        parts.append(f"  r/{row['subreddit']}: {row['posts']:,} posts, {row['comments']:,} comments")

    date_range = conn.execute(
        "SELECT MIN(created_utc) as mn, MAX(created_utc) as mx FROM posts"
    ).fetchone()
    parts.append(f"\nDate range: {_ts_to_date(date_range['mn'])} to {_ts_to_date(date_range['mx'])}")

    conn.close()
    return "\n".join(parts)


@mcp.tool()
def sql_query(query: str) -> str:
    """Run a read-only SQL query directly against the database.
    Use for custom aggregations, joins, or anything the other tools don't cover.

    Tables: posts (id, subreddit, author, title, selftext, score, num_comments, created_utc, permalink)
            comments (id, subreddit, author, body, score, created_utc, link_id, parent_id, permalink)

    Args:
        query: A SELECT query. Only SELECT is allowed.
    """
    q = query.strip().rstrip(";")
    if not q.upper().startswith("SELECT"):
        return "Error: Only SELECT queries are allowed."

    conn = _connect()
    try:
        rows = conn.execute(q).fetchall()
        if not rows:
            return "Query returned no results."

        # Format as table
        cols = rows[0].keys()
        header = " | ".join(cols)
        separator = "-|-".join("-" * len(c) for c in cols)
        lines = [header, separator]
        for row in rows[:100]:
            vals = []
            for col in cols:
                v = str(row[col])
                if len(v) > 200:
                    v = v[:200] + "..."
                vals.append(v)
            lines.append(" | ".join(vals))

        result = "\n".join(lines)
        if len(rows) > 100:
            result += f"\n\n... and {len(rows) - 100} more rows (showing first 100)"
        return result
    except Exception as e:
        return f"SQL error: {e}"
    finally:
        conn.close()


if __name__ == "__main__":
    import sys
    if "--sse" in sys.argv:
        os.environ.setdefault("MCP_HOST", "127.0.0.1")
        os.environ.setdefault("MCP_PORT", "8765")
        mcp.run(transport="sse")
    else:
        mcp.run()
