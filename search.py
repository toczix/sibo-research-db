#!/usr/bin/env python3
"""Search the Reddit SQLite database for symptoms, treatments, and patterns."""

import argparse
import sqlite3
import sys
from datetime import datetime, timezone


DB_PATH = "reddit.db"


def connect(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def ts_to_date(ts):
    try:
        return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d")
    except (ValueError, TypeError, OSError):
        return "unknown"


def search_posts(conn, query: str, limit: int = 30, min_score: int = 0,
                 subreddit: str = None):
    """Full-text search across post titles and body text."""
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
           p.created_utc, p.permalink,
           rank
    FROM posts_fts fts
    JOIN posts p ON p.rowid = fts.rowid
    WHERE posts_fts MATCH ?
    {where_extra}
    ORDER BY rank
    LIMIT ?
    """
    return conn.execute(sql, params).fetchall()


def search_comments(conn, query: str, limit: int = 50, min_score: int = 0,
                    subreddit: str = None):
    """Full-text search across comment bodies."""
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
           c.created_utc, c.link_id, c.permalink,
           rank
    FROM comments_fts fts
    JOIN comments c ON c.rowid = fts.rowid
    WHERE comments_fts MATCH ?
    {where_extra}
    ORDER BY rank
    LIMIT ?
    """
    return conn.execute(sql, params).fetchall()


def get_thread(conn, post_id: str):
    """Get a post and all its comments."""
    post_id_clean = post_id.replace("t3_", "")
    post = conn.execute("SELECT * FROM posts WHERE id = ?", (post_id_clean,)).fetchone()
    comments = conn.execute(
        "SELECT * FROM comments WHERE link_id = ? OR link_id = ? ORDER BY score DESC",
        (f"t3_{post_id_clean}", post_id_clean)
    ).fetchall()
    return post, comments


def print_post(row, show_body=True):
    date = ts_to_date(row["created_utc"])
    print(f"\n{'='*80}")
    print(f"[{row['score']:+d} | {row['num_comments']} comments | {date}] r/{row['subreddit']}")
    print(f"  {row['title']}")
    print(f"  https://reddit.com{row['permalink']}")
    if show_body and row["selftext"]:
        body = row["selftext"][:500]
        if len(row["selftext"]) > 500:
            body += "..."
        print(f"\n  {body}")


def print_comment(row):
    date = ts_to_date(row["created_utc"])
    body = row["body"][:400]
    if len(row["body"]) > 400:
        body += "..."
    print(f"\n{'─'*80}")
    print(f"[{row['score']:+d} | {date}] u/{row['author']} in r/{row['subreddit']}")
    print(f"  {body}")
    if row["permalink"]:
        print(f"  https://reddit.com{row['permalink']}")


def cmd_search(args):
    conn = connect(args.db)
    query = args.query

    print(f"\n=== POSTS matching: {query} ===")
    posts = search_posts(conn, query, limit=args.limit, min_score=args.min_score,
                         subreddit=args.subreddit)
    if not posts:
        print("  No matching posts found.")
    for row in posts:
        print_post(row, show_body=args.verbose)

    print(f"\n\n=== COMMENTS matching: {query} ===")
    comments = search_comments(conn, query, limit=args.limit, min_score=args.min_score,
                               subreddit=args.subreddit)
    if not comments:
        print("  No matching comments found.")
    for row in comments:
        print_comment(row)

    conn.close()


def cmd_thread(args):
    conn = connect(args.db)
    post, comments = get_thread(conn, args.post_id)
    if not post:
        print(f"Post {args.post_id} not found.")
        sys.exit(1)

    print_post(dict(post), show_body=True)
    print(f"\n--- {len(comments)} comments ---")
    for c in comments[:args.limit]:
        print_comment(c)
    conn.close()


def cmd_stats(args):
    conn = connect(args.db)
    print("\n=== Database Stats ===")

    for table in ("posts", "comments"):
        row = conn.execute(f"SELECT COUNT(*) as cnt FROM {table}").fetchone()
        print(f"  {table}: {row['cnt']:,}")

    print("\n  Subreddits (posts):")
    for row in conn.execute(
        "SELECT subreddit, COUNT(*) as cnt FROM posts GROUP BY subreddit ORDER BY cnt DESC"
    ):
        print(f"    r/{row['subreddit']}: {row['cnt']:,}")

    print("\n  Subreddits (comments):")
    for row in conn.execute(
        "SELECT subreddit, COUNT(*) as cnt FROM comments GROUP BY subreddit ORDER BY cnt DESC"
    ):
        print(f"    r/{row['subreddit']}: {row['cnt']:,}")

    print("\n  Date range (posts):")
    row = conn.execute(
        "SELECT MIN(created_utc) as mn, MAX(created_utc) as mx FROM posts"
    ).fetchone()
    print(f"    {ts_to_date(row['mn'])} to {ts_to_date(row['mx'])}")

    conn.close()


def cmd_export(args):
    """Export search results to a JSONL file for further analysis."""
    import json
    conn = connect(args.db)
    query = args.query
    out_path = args.output

    results = []

    posts = search_posts(conn, query, limit=args.limit, min_score=args.min_score,
                         subreddit=args.subreddit)
    for row in posts:
        results.append({
            "type": "post",
            "id": row["id"],
            "subreddit": row["subreddit"],
            "title": row["title"],
            "selftext": row["selftext"],
            "score": row["score"],
            "num_comments": row["num_comments"],
            "date": ts_to_date(row["created_utc"]),
            "permalink": f"https://reddit.com{row['permalink']}",
        })

    comments = search_comments(conn, query, limit=args.limit, min_score=args.min_score,
                               subreddit=args.subreddit)
    for row in comments:
        results.append({
            "type": "comment",
            "id": row["id"],
            "subreddit": row["subreddit"],
            "author": row["author"],
            "body": row["body"],
            "score": row["score"],
            "date": ts_to_date(row["created_utc"]),
            "permalink": f"https://reddit.com{row['permalink']}" if row["permalink"] else "",
        })

    with open(out_path, "w") as f:
        for r in results:
            f.write(json.dumps(r) + "\n")

    print(f"Exported {len(results)} results to {out_path}")
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="Search Reddit symptom database")
    parser.add_argument("--db", default=DB_PATH, help="SQLite database path")
    sub = parser.add_subparsers(dest="command")

    # search
    sp = sub.add_parser("search", help="Full-text search posts and comments")
    sp.add_argument("query", help='FTS5 query (e.g. "bloating AND rifaximin")')
    sp.add_argument("-n", "--limit", type=int, default=20)
    sp.add_argument("--min-score", type=int, default=0)
    sp.add_argument("--subreddit", type=str, default=None)
    sp.add_argument("-v", "--verbose", action="store_true", help="Show post bodies")

    # thread
    sp = sub.add_parser("thread", help="View a full thread by post ID")
    sp.add_argument("post_id", help="Reddit post ID (e.g. 3ge7tm)")
    sp.add_argument("-n", "--limit", type=int, default=50)

    # stats
    sub.add_parser("stats", help="Show database statistics")

    # export
    sp = sub.add_parser("export", help="Export search results to JSONL")
    sp.add_argument("query", help="FTS5 query")
    sp.add_argument("-o", "--output", default="results.jsonl")
    sp.add_argument("-n", "--limit", type=int, default=200)
    sp.add_argument("--min-score", type=int, default=0)
    sp.add_argument("--subreddit", type=str, default=None)

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    {"search": cmd_search, "thread": cmd_thread, "stats": cmd_stats,
     "export": cmd_export}[args.command](args)


if __name__ == "__main__":
    main()
