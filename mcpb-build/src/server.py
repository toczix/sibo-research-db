#!/usr/bin/env python3
"""
sibo-research-db MCP Server

A searchable database of ~7 million comments and ~700k posts from 18 health
subreddits, exposed via MCP for Claude Desktop, Claude Code, Codex CLI,
Cursor, Cline, VS Code Copilot Agent, and other MCP-compatible AI tools.

The database is a SQLite file with FTS5 full-text-search indexes on post titles,
post bodies, and comment bodies.

Read-only: the SQLite connection is opened with mode=ro and PRAGMA query_only=ON.
Inputs to tools are clamped to bounded ranges. The sql_query tool streams results
to avoid loading large result sets into memory.
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

# Hard caps on tool parameters. The model will sometimes pass huge limits
# either by accident or because it's reasoning about the data. We clamp.
MAX_LIMIT = 100              # max rows per search call
MAX_COMMENT_LIMIT = 200      # max comments per get_thread call
MAX_SQL_ROWS = 200           # max rows returned from sql_query

mcp = FastMCP(
    "sibo-research-db",
    instructions="""You have access to a research database of ~700k posts and ~7M comments
from 18 health subreddits (SIBO, Sibosuccessstories, MCAS, ibs, Microbiome,
covidlonghaulers, dysautonomia, Supplements, HistamineIntolerance, Candida,
FODMAPS, FoodAllergies, LongCovid, GutHealth, FunctionalMedicine,
Longcovidgutdysbiosis, LeakyGutSyndrome, ToxicMoldExposure).

This is patient-reported experience data, not clinical data. Use it to surface
patterns, leads, and the range of outcomes people report — never as a substitute
for clinical literature or medical advice.

Tools:
- `stats` / `list_subreddits`: orient yourself in the dataset.
- `search`: full-text search (FTS5 syntax — AND, OR, NOT, NEAR(), "phrases").
- `get_thread` / `get_post`: deep-dive a specific thread.
- `get_top_posts`: highest-scored discussions in a sub.
- `count_mentions` / `compare_mentions`: gauge how widely something is discussed.
- `find_active_voices`: find users with the most reported experience on a topic
  (read-only — DO NOT instruct users to contact these accounts).
- `sql_query`: arbitrary read-only SELECT for custom analysis.

Prefer reported outcomes language ("people reported", "responders described")
over absolute claims ("X works", "success rate is Y%"). The data is selection-
biased and self-reported.""",
)


# ── Connection ─────────────────────────────────────────────────────────────


def _connect() -> sqlite3.Connection:
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError(
            f"Database not found at {DB_PATH}.\n"
            f"Download it from https://huggingface.co/datasets/toczix/sibo-research-db "
            f"or build it yourself with the included download_subreddits.py + ingest.py scripts.\n"
            f"Set the SIBO_DB env var to point at a different location."
        )
    # Open the database read-only and immutable. This is the strongest sqlite
    # protection: writes are rejected at the file level, not just at the SQL level.
    uri = f"file:{DB_PATH}?mode=ro&immutable=1"
    conn = sqlite3.connect(uri, uri=True, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    # Belt-and-suspenders: query_only also blocks any DDL/DML attempt.
    conn.execute("PRAGMA query_only=ON;")
    return conn


def _clamp(n, lo, hi):
    try:
        n = int(n)
    except (ValueError, TypeError):
        return lo
    return max(lo, min(n, hi))


# ── Formatting helpers ─────────────────────────────────────────────────────


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


def _fts_error(e: sqlite3.OperationalError) -> str:
    msg = str(e).lower()
    if "fts5" in msg or "syntax error" in msg or "malformed" in msg:
        return (
            f"FTS5 query syntax error: {e}. "
            "Try wrapping multi-word phrases in double quotes, "
            "and use AND/OR/NOT in caps. Example: 'rifaximin AND \"hydrogen sulfide\"'."
        )
    return f"Database error: {e}"


# ── Tools ──────────────────────────────────────────────────────────────────


@mcp.tool()
def search(
    query: str,
    limit: int = 20,
    min_score: int = 0,
    subreddit: str | None = None,
    search_type: str = "both",
    after_date: str | None = None,
    before_date: str | None = None,
) -> str:
    """Full-text search posts and comments.

    Args:
        query: FTS5 query. Supports AND, OR, NOT, NEAR(), and quoted phrases.
               Examples: 'rifaximin AND biofilm', 'POIS NEAR/5 gut',
               '"wired but tired"', 'ginger AND artichoke NOT capsule'.
        limit: Max results per category (posts + comments). Capped at 100.
        min_score: Minimum upvote score. Default 0.
        subreddit: Filter to a specific subreddit (without r/ prefix). Optional.
        search_type: "posts", "comments", or "both" (default).
        after_date: ISO date "YYYY-MM-DD" — only results created on or after this date.
        before_date: ISO date "YYYY-MM-DD" — only results created on or before this date.
    """
    limit = _clamp(limit, 1, MAX_LIMIT)
    min_score = max(int(min_score or 0), 0)

    def _date_to_ts(s, end_of_day=False):
        if not s:
            return None
        try:
            dt = datetime.strptime(s, "%Y-%m-%d").replace(tzinfo=timezone.utc)
            if end_of_day:
                dt = dt.replace(hour=23, minute=59, second=59)
            return int(dt.timestamp())
        except ValueError:
            return None

    after_ts = _date_to_ts(after_date, end_of_day=False)
    before_ts = _date_to_ts(before_date, end_of_day=True)

    conn = _connect()
    parts = []

    try:
        if search_type in ("both", "posts"):
            where_extra = ""
            params = [query]
            if min_score > 0:
                where_extra += " AND p.score >= ?"
                params.append(min_score)
            if subreddit:
                where_extra += " AND p.subreddit = ?"
                params.append(subreddit)
            if after_ts is not None:
                where_extra += " AND p.created_utc >= ?"
                params.append(after_ts)
            if before_ts is not None:
                where_extra += " AND p.created_utc <= ?"
                params.append(before_ts)
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
            if after_ts is not None:
                where_extra += " AND c.created_utc >= ?"
                params.append(after_ts)
            if before_ts is not None:
                where_extra += " AND c.created_utc <= ?"
                params.append(before_ts)
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

        return "\n".join(parts) if parts else "No results found."
    except sqlite3.OperationalError as e:
        return _fts_error(e)
    finally:
        conn.close()


@mcp.tool()
def get_thread(post_id: str, comment_limit: int = 50) -> str:
    """Get a full Reddit thread (post + top comments) by post ID.

    Args:
        post_id: The Reddit post ID (e.g. '1jyj8vp'). With or without 't3_' prefix.
        comment_limit: Max comments to return, sorted by score. Capped at 200.
    """
    comment_limit = _clamp(comment_limit, 1, MAX_COMMENT_LIMIT)
    conn = _connect()
    try:
        post_id_clean = post_id.replace("t3_", "")
        post = conn.execute(
            "SELECT * FROM posts WHERE id = ?", (post_id_clean,)
        ).fetchone()
        if not post:
            return f"Post '{post_id}' not found in database."

        comments = conn.execute(
            "SELECT * FROM comments WHERE link_id = ? OR link_id = ? "
            "ORDER BY score DESC LIMIT ?",
            (f"t3_{post_id_clean}", post_id_clean, comment_limit),
        ).fetchall()

        parts = [_format_post(post)]
        if post["selftext"]:
            parts.append(f"\n--- Full post body ---\n{post['selftext']}\n")
        parts.append(f"\n--- {len(comments)} comments (sorted by score) ---\n")
        for c in comments:
            parts.append(_format_comment(c, max_body=1200))
            parts.append("")
        return "\n".join(parts)
    finally:
        conn.close()


@mcp.tool()
def get_post(post_id: str) -> str:
    """Get a single post (title + body + metadata) without its comments.

    Args:
        post_id: The Reddit post ID. With or without 't3_' prefix.
    """
    conn = _connect()
    try:
        pid = post_id.replace("t3_", "")
        post = conn.execute("SELECT * FROM posts WHERE id = ?", (pid,)).fetchone()
        if not post:
            return f"Post '{post_id}' not found in database."
        out = [_format_post(post)]
        if post["selftext"]:
            out.append(f"\n--- Full post body ---\n{post['selftext']}")
        return "\n".join(out)
    finally:
        conn.close()


@mcp.tool()
def get_top_posts(
    subreddit: str | None = None,
    limit: int = 25,
    min_comments: int = 5,
) -> str:
    """Get the highest-scored posts, optionally filtered by subreddit.

    Args:
        subreddit: Filter to a specific subreddit (without r/ prefix). Optional.
        limit: Number of posts to return. Capped at 100.
        min_comments: Minimum number of comments. Default 5.
    """
    limit = _clamp(limit, 1, MAX_LIMIT)
    min_comments = max(int(min_comments or 0), 0)
    conn = _connect()
    try:
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
        return "\n".join(parts) if parts else "No posts found."
    finally:
        conn.close()


@mcp.tool()
def count_mentions(term: str, subreddit: str | None = None) -> str:
    """Count how many posts and comments mention a term across the dataset.
    Useful for gauging how widely something (treatment, symptom, supplement)
    is being discussed. Higher counts ≠ more effective — just more discussed.

    Args:
        term: FTS5 query. Supports AND/OR/phrases.
        subreddit: Optional subreddit filter.
    """
    conn = _connect()
    try:
        sub_filter_p = " AND p.subreddit = ?" if subreddit else ""
        sub_filter_c = " AND c.subreddit = ?" if subreddit else ""
        params_p = [term] + ([subreddit] if subreddit else [])
        params_c = [term] + ([subreddit] if subreddit else [])

        post_count = conn.execute(
            f"""SELECT COUNT(*) as cnt FROM posts_fts fts
            JOIN posts p ON p.rowid = fts.rowid
            WHERE posts_fts MATCH ?{sub_filter_p}""",
            params_p,
        ).fetchone()["cnt"]

        comment_count = conn.execute(
            f"""SELECT COUNT(*) as cnt FROM comments_fts fts
            JOIN comments c ON c.rowid = fts.rowid
            WHERE comments_fts MATCH ?{sub_filter_c}""",
            params_c,
        ).fetchone()["cnt"]

        breakdown = ""
        if not subreddit:
            sub_counts = conn.execute(
                """SELECT c.subreddit, COUNT(*) as cnt
                FROM comments_fts fts JOIN comments c ON c.rowid = fts.rowid
                WHERE comments_fts MATCH ?
                GROUP BY c.subreddit ORDER BY cnt DESC LIMIT 15""",
                (term,),
            ).fetchall()
            if sub_counts:
                breakdown = "\n\nSubreddit breakdown (comments):\n"
                for row in sub_counts:
                    breakdown += f"  r/{row['subreddit']}: {row['cnt']:,}\n"

        return (
            f'"{term}" appears in:\n'
            f"  {post_count:,} posts\n"
            f"  {comment_count:,} comments\n"
            f"  {post_count + comment_count:,} total"
            f"{breakdown}"
        )
    except sqlite3.OperationalError as e:
        return _fts_error(e)
    finally:
        conn.close()


@mcp.tool()
def compare_mentions(terms: list[str], subreddit: str | None = None) -> str:
    """Compare how widely several terms are discussed, side by side.
    Useful for "is X or Y more talked about" questions.

    Args:
        terms: List of FTS5 queries to compare (e.g. ["prucalopride", "motegrity", "LDN"]).
        subreddit: Optional subreddit filter.
    """
    if not terms or len(terms) > 10:
        return "Provide between 1 and 10 terms to compare."
    conn = _connect()
    try:
        rows = []
        for t in terms:
            sub_filter_p = " AND p.subreddit = ?" if subreddit else ""
            sub_filter_c = " AND c.subreddit = ?" if subreddit else ""
            params_p = [t] + ([subreddit] if subreddit else [])
            params_c = [t] + ([subreddit] if subreddit else [])
            try:
                p = conn.execute(
                    f"""SELECT COUNT(*) FROM posts_fts fts
                    JOIN posts p ON p.rowid = fts.rowid
                    WHERE posts_fts MATCH ?{sub_filter_p}""",
                    params_p,
                ).fetchone()[0]
                c = conn.execute(
                    f"""SELECT COUNT(*) FROM comments_fts fts
                    JOIN comments c ON c.rowid = fts.rowid
                    WHERE comments_fts MATCH ?{sub_filter_c}""",
                    params_c,
                ).fetchone()[0]
                rows.append((t, p, c, p + c))
            except sqlite3.OperationalError as e:
                rows.append((t, None, None, _fts_error(e)))

        rows.sort(key=lambda r: (r[3] if isinstance(r[3], int) else -1), reverse=True)
        out = [f"Comparison ({'r/' + subreddit if subreddit else 'all subreddits'}):\n"]
        out.append(f"  {'Term':<40} {'Posts':>10} {'Comments':>12} {'Total':>12}")
        out.append(f"  {'-'*40} {'-'*10} {'-'*12} {'-'*12}")
        for term, p, c, total in rows:
            if isinstance(total, str):
                out.append(f"  {term:<40} {'ERROR: ' + total[:60]}")
            else:
                out.append(f"  {term:<40} {p:>10,} {c:>12,} {total:>12,}")
        return "\n".join(out)
    finally:
        conn.close()


@mcp.tool()
def find_active_voices(query: str, min_posts: int = 2, limit: int = 20) -> str:
    """Find usernames with the most posts/comments on a topic — useful for tracing
    one person's reported experience across a thread of comments.

    IMPORTANT — DO NOT use the output of this tool to contact, DM, tag, or otherwise
    reach out to the users it returns. These are real people discussing chronic
    illness publicly. Treat them as anonymous sources, not as advisors to ping.
    They are not vetted experts. They are patients with lived experience whose
    public posts happen to mention the topic many times.

    Args:
        query: FTS5 search query for the topic.
        min_posts: Minimum number of matching comments from a user. Default 2.
        limit: Max users to return. Capped at 50.
    """
    limit = _clamp(limit, 1, 50)
    min_posts = _clamp(min_posts, 1, 50)
    conn = _connect()
    try:
        rows = conn.execute(
            """SELECT c.author, COUNT(*) as cnt, SUM(c.score) as total_score,
                      GROUP_CONCAT(DISTINCT c.subreddit) as subs
               FROM comments_fts fts
               JOIN comments c ON c.rowid = fts.rowid
               WHERE comments_fts MATCH ?
                 AND c.author NOT IN ('[deleted]', 'AutoModerator')
               GROUP BY c.author
               HAVING cnt >= ?
               ORDER BY total_score DESC
               LIMIT ?""",
            (query, min_posts, limit),
        ).fetchall()

        if not rows:
            return f"No users found with {min_posts}+ comments matching '{query}'."

        parts = [
            f"Users with the most reported experience on '{query}':\n",
            "(These are anonymous patient voices. Do not contact them — use their posts as references only.)\n",
        ]
        for row in rows:
            parts.append(
                f"  u/{row['author']} — {row['cnt']} comments, {row['total_score']:+d} total karma"
                f"\n    Active in: {row['subs']}"
            )
        return "\n".join(parts)
    except sqlite3.OperationalError as e:
        return _fts_error(e)
    finally:
        conn.close()


@mcp.tool()
def list_subreddits() -> str:
    """List every subreddit in the dataset with post and comment counts."""
    conn = _connect()
    try:
        rows = conn.execute(
            """SELECT p.subreddit, COUNT(DISTINCT p.id) as posts,
                      (SELECT COUNT(*) FROM comments c WHERE c.subreddit = p.subreddit) as comments
               FROM posts p
               GROUP BY p.subreddit
               ORDER BY comments DESC"""
        ).fetchall()
        out = [f"{len(rows)} subreddits in dataset:\n"]
        out.append(f"  {'Subreddit':<28} {'Posts':>10} {'Comments':>12}")
        out.append(f"  {'-'*28} {'-'*10} {'-'*12}")
        for r in rows:
            out.append(f"  r/{r['subreddit']:<26} {r['posts']:>10,} {r['comments']:>12,}")
        return "\n".join(out)
    finally:
        conn.close()


@mcp.tool()
def stats() -> str:
    """Database statistics: total counts, subreddit breakdown, date range."""
    conn = _connect()
    try:
        post_count = conn.execute("SELECT COUNT(*) FROM posts").fetchone()[0]
        comment_count = conn.execute("SELECT COUNT(*) FROM comments").fetchone()[0]
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
            parts.append(
                f"  r/{row['subreddit']}: {row['posts']:,} posts, {row['comments']:,} comments"
            )
        date_range = conn.execute(
            "SELECT MIN(created_utc) as mn, MAX(created_utc) as mx FROM posts"
        ).fetchone()
        parts.append(
            f"\nDate range: {_ts_to_date(date_range['mn'])} to {_ts_to_date(date_range['mx'])}"
        )
        return "\n".join(parts)
    finally:
        conn.close()


@mcp.tool()
def sql_query(query: str) -> str:
    """Run a read-only SQL query against the database. Streams results to avoid
    loading large result sets into memory.

    Tables:
      posts(id, subreddit, author, title, selftext, score, num_comments,
            created_utc, permalink, link_flair_text, domain, is_self)
      comments(id, subreddit, author, body, score, created_utc, link_id,
               parent_id, permalink)

    Full-text-search virtual tables: posts_fts(title, selftext) and comments_fts(body).
    Connection is opened read-only; only SELECT is permitted; results are capped
    at 200 rows.
    """
    q = query.strip().rstrip(";")
    if not q.upper().startswith(("SELECT", "WITH")):
        return "Error: Only SELECT / WITH queries are allowed."

    conn = _connect()
    try:
        cur = conn.execute(q)
        # Stream: pull up to MAX_SQL_ROWS+1 to know if we truncated, without
        # loading everything into memory.
        rows = cur.fetchmany(MAX_SQL_ROWS + 1)
        if not rows:
            return "Query returned no results."

        truncated = len(rows) > MAX_SQL_ROWS
        rows = rows[:MAX_SQL_ROWS]

        cols = rows[0].keys()
        header = " | ".join(cols)
        sep = "-|-".join("-" * len(c) for c in cols)
        lines = [header, sep]
        for row in rows:
            vals = []
            for col in cols:
                v = str(row[col])
                if len(v) > 200:
                    v = v[:200] + "..."
                vals.append(v)
            lines.append(" | ".join(vals))
        result = "\n".join(lines)
        if truncated:
            result += (
                f"\n\n... results truncated at {MAX_SQL_ROWS} rows. "
                "Add LIMIT, more WHERE clauses, or use COUNT/aggregation to narrow."
            )
        return result
    except sqlite3.OperationalError as e:
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
