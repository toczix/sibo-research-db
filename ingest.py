#!/usr/bin/env python3
"""Ingest Reddit JSONL dumps (from arctic-shift) into a SQLite database with FTS5."""

import argparse
import json
import sqlite3
import sys
import time
from pathlib import Path

POSTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    id TEXT PRIMARY KEY,
    subreddit TEXT,
    author TEXT,
    title TEXT,
    selftext TEXT,
    score INTEGER,
    num_comments INTEGER,
    created_utc INTEGER,
    permalink TEXT,
    link_flair_text TEXT,
    domain TEXT,
    is_self INTEGER
);
"""

COMMENTS_SCHEMA = """
CREATE TABLE IF NOT EXISTS comments (
    id TEXT PRIMARY KEY,
    subreddit TEXT,
    author TEXT,
    body TEXT,
    score INTEGER,
    created_utc INTEGER,
    link_id TEXT,
    parent_id TEXT,
    permalink TEXT
);
"""

FTS_POSTS = """
CREATE VIRTUAL TABLE IF NOT EXISTS posts_fts USING fts5(
    title, selftext, content=posts, content_rowid=rowid
);
"""

FTS_COMMENTS = """
CREATE VIRTUAL TABLE IF NOT EXISTS comments_fts USING fts5(
    body, content=comments, content_rowid=rowid
);
"""

INDEXES = [
    "CREATE INDEX IF NOT EXISTS idx_posts_subreddit ON posts(subreddit);",
    "CREATE INDEX IF NOT EXISTS idx_posts_score ON posts(score);",
    "CREATE INDEX IF NOT EXISTS idx_posts_created ON posts(created_utc);",
    "CREATE INDEX IF NOT EXISTS idx_comments_subreddit ON comments(subreddit);",
    "CREATE INDEX IF NOT EXISTS idx_comments_link_id ON comments(link_id);",
    "CREATE INDEX IF NOT EXISTS idx_comments_score ON comments(score);",
    "CREATE INDEX IF NOT EXISTS idx_comments_created ON comments(created_utc);",
]


def init_db(db_path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA synchronous=NORMAL;")
    conn.execute("PRAGMA cache_size=-64000;")  # 64MB cache
    conn.execute(POSTS_SCHEMA)
    conn.execute(COMMENTS_SCHEMA)
    conn.execute(FTS_POSTS)
    conn.execute(FTS_COMMENTS)
    for idx in INDEXES:
        conn.execute(idx)
    conn.commit()
    return conn


def ingest_posts(conn: sqlite3.Connection, filepath: str):
    print(f"Ingesting posts from {filepath}...")
    count = 0
    batch = []
    start = time.time()

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue

            batch.append((
                rec.get("id", ""),
                rec.get("subreddit", ""),
                rec.get("author", ""),
                rec.get("title", ""),
                rec.get("selftext", ""),
                rec.get("score", 0),
                rec.get("num_comments", 0),
                rec.get("created_utc", 0),
                rec.get("permalink", ""),
                rec.get("link_flair_text", ""),
                rec.get("domain", ""),
                1 if rec.get("is_self") else 0,
            ))

            if len(batch) >= 5000:
                _flush_posts(conn, batch)
                count += len(batch)
                batch = []
                elapsed = time.time() - start
                print(f"  {count:,} posts ({elapsed:.1f}s)", end="\r")

    if batch:
        _flush_posts(conn, batch)
        count += len(batch)

    elapsed = time.time() - start
    print(f"  {count:,} posts ingested in {elapsed:.1f}s")


def _flush_posts(conn, batch):
    conn.executemany(
        "INSERT OR IGNORE INTO posts VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", batch
    )
    conn.executemany(
        "INSERT INTO posts_fts(rowid, title, selftext) "
        "SELECT rowid, title, selftext FROM posts WHERE id = ?",
        [(r[0],) for r in batch],
    )
    conn.commit()


def ingest_comments(conn: sqlite3.Connection, filepath: str):
    print(f"Ingesting comments from {filepath}...")
    count = 0
    batch = []
    start = time.time()

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue

            body = rec.get("body", "")
            if body in ("[deleted]", "[removed]", ""):
                continue

            batch.append((
                rec.get("id", ""),
                rec.get("subreddit", ""),
                rec.get("author", ""),
                body,
                rec.get("score", 0),
                rec.get("created_utc", 0),
                rec.get("link_id", ""),
                rec.get("parent_id", ""),
                rec.get("permalink", ""),
            ))

            if len(batch) >= 10000:
                _flush_comments(conn, batch)
                count += len(batch)
                batch = []
                elapsed = time.time() - start
                print(f"  {count:,} comments ({elapsed:.1f}s)", end="\r")

    if batch:
        _flush_comments(conn, batch)
        count += len(batch)

    elapsed = time.time() - start
    print(f"  {count:,} comments ingested in {elapsed:.1f}s")


def _flush_comments(conn, batch):
    conn.executemany(
        "INSERT OR IGNORE INTO comments VALUES (?,?,?,?,?,?,?,?,?)", batch
    )
    conn.executemany(
        "INSERT INTO comments_fts(rowid, body) "
        "SELECT rowid, body FROM comments WHERE id = ?",
        [(r[0],) for r in batch],
    )
    conn.commit()


def main():
    parser = argparse.ArgumentParser(description="Ingest Reddit JSONL into SQLite")
    parser.add_argument("--db", default="reddit.db", help="SQLite database path")
    parser.add_argument("--posts", help="Path to posts JSONL file")
    parser.add_argument("--comments", help="Path to comments JSONL file")
    args = parser.parse_args()

    if not args.posts and not args.comments:
        parser.error("Provide at least one of --posts or --comments")

    conn = init_db(args.db)

    if args.posts:
        ingest_posts(conn, args.posts)
    if args.comments:
        ingest_comments(conn, args.comments)

    print("Building FTS index optimization...")
    conn.execute("INSERT INTO posts_fts(posts_fts) VALUES('optimize');")
    conn.execute("INSERT INTO comments_fts(comments_fts) VALUES('optimize');")
    conn.commit()

    row = conn.execute("SELECT COUNT(*) FROM posts").fetchone()
    print(f"Total posts in DB: {row[0]:,}")
    row = conn.execute("SELECT COUNT(*) FROM comments").fetchone()
    print(f"Total comments in DB: {row[0]:,}")

    conn.close()
    print("Done.")


if __name__ == "__main__":
    main()
