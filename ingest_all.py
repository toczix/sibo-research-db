#!/usr/bin/env python3
"""Ingest all downloaded subreddit JSONL files into the SQLite database."""

import glob
import os
import re
import subprocess
import sys

DOWNLOAD_DIR = os.path.expanduser("~/Downloads")
DB_PATH = "reddit.db"


def find_subreddit_files():
    """Find all r_*_posts.jsonl and r_*_comments.jsonl pairs in Downloads."""
    posts_files = glob.glob(os.path.join(DOWNLOAD_DIR, "r_*_posts.jsonl"))
    subs = {}
    for pf in posts_files:
        basename = os.path.basename(pf)
        match = re.match(r"r_(.+)_posts\.jsonl", basename)
        if match:
            sub = match.group(1)
            cf = os.path.join(DOWNLOAD_DIR, f"r_{sub}_comments.jsonl")
            subs[sub] = {
                "posts": pf,
                "comments": cf if os.path.exists(cf) else None,
                "posts_size": os.path.getsize(pf),
                "comments_size": os.path.getsize(cf) if os.path.exists(cf) else 0,
            }
    return subs


def main():
    subs = find_subreddit_files()
    if not subs:
        print("No subreddit files found in Downloads.")
        sys.exit(1)

    print(f"Found {len(subs)} subreddits to ingest:\n")
    for sub, info in sorted(subs.items()):
        ps = info["posts_size"] / (1024 * 1024)
        cs = info["comments_size"] / (1024 * 1024)
        status = "posts + comments" if info["comments"] else "posts only"
        print(f"  r/{sub}: {ps:.1f}MB posts, {cs:.1f}MB comments ({status})")

    print(f"\nIngesting into {DB_PATH}...\n")

    for i, (sub, info) in enumerate(sorted(subs.items()), 1):
        print(f"[{i}/{len(subs)}] r/{sub}")
        cmd = ["python3", "ingest.py", "--db", DB_PATH, "--posts", info["posts"]]
        if info["comments"]:
            cmd.extend(["--comments", info["comments"]])
        subprocess.run(cmd)
        print()

    print("All subreddits ingested. Run 'python3 search.py stats' to see totals.")


if __name__ == "__main__":
    main()
