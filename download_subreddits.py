#!/usr/bin/env python3
"""Download subreddit posts and comments from arctic-shift (a public Reddit archive).

Usage:
  python3 download_subreddits.py                  # download all defaults
  python3 download_subreddits.py SIBO MCAS        # download specific subs
"""

import json
import os
import sys
import time
import urllib.request
import urllib.parse

BASE = "https://arctic-shift.photon-reddit.com"
DOWNLOAD_DIR = os.environ.get("SIBO_DOWNLOAD_DIR", os.path.expanduser("~/Downloads"))

# 17 health subreddits covered by sibo-research-db
SUBREDDITS = [
    "SIBO",
    "MCAS",
    "ibs",
    "Microbiome",
    "covidlonghaulers",
    "dysautonomia",
    "Supplements",
    "HistamineIntolerance",
    "Candida",
    "FODMAPS",
    "FoodAllergies",
    "LongCovid",
    "GutHealth",
    "FunctionalMedicine",
    "Longcovidgutdysbiosis",
    "LeakyGutSyndrome",
    "ToxicMoldExposure",
    "Sibosuccessstories",
]

# 2005-01-01 in ms (Reddit's birth roughly)
START_MS = 1104537600000

# Large subs limited to a more recent start to keep the DB manageable
START_OVERRIDES = {
    "ibs": 1621209600000,         # 2021-05-17
    "Supplements": 1621209600000, # 2021-05-17
}


def fetch_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "sibo-research-db/1.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        return json.loads(resp.read())


def download_type(subreddit, content_type, out_path):
    """Download all posts or comments for a subreddit using pagination."""
    base_url = f"{BASE}/api/{content_type}/search?subreddit={urllib.parse.quote(subreddit)}"
    current_ms = START_OVERRIDES.get(subreddit, START_MS)
    total = 0
    start = time.time()

    with open(out_path, "w") as f:
        while True:
            url = f"{base_url}&limit=auto&sort=asc&after={current_ms}&meta-app=download-tool"

            try:
                result = fetch_json(url)
            except Exception as e:
                print(f"\n  Error: {e}, retrying in 3s...")
                time.sleep(3)
                continue

            if result.get("error"):
                print(f"\n  API error: {result['error']}")
                break

            data = result.get("data")
            if not data:
                break

            for item in data:
                f.write(json.dumps(item) + "\n")

            total += len(data)
            last_utc = data[-1].get("created_utc", 0)
            current_ms = int(last_utc * 1000) if last_utc < 1e12 else int(last_utc)
            elapsed = time.time() - start
            print(f"  {total:,} {content_type} ({elapsed:.0f}s)", end="\r")

            time.sleep(0.05)

    elapsed = time.time() - start
    print(f"  {total:,} {content_type} in {elapsed:.0f}s        ")
    return total


def main():
    subs = SUBREDDITS
    if len(sys.argv) > 1:
        subs = sys.argv[1:]

    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    print(f"Downloading {len(subs)} subreddits to {DOWNLOAD_DIR}\n")

    for i, sub in enumerate(subs, 1):
        posts_path = os.path.join(DOWNLOAD_DIR, f"r_{sub}_posts.jsonl")
        comments_path = os.path.join(DOWNLOAD_DIR, f"r_{sub}_comments.jsonl")

        if os.path.exists(posts_path) and os.path.exists(comments_path):
            psize = os.path.getsize(posts_path)
            csize = os.path.getsize(comments_path)
            if psize > 0 and csize > 0:
                print(f"[{i}/{len(subs)}] r/{sub} — already downloaded, skipping")
                continue

        print(f"[{i}/{len(subs)}] r/{sub}")

        if not os.path.exists(posts_path) or os.path.getsize(posts_path) == 0:
            download_type(sub, "posts", posts_path)
        else:
            print(f"  posts file exists, skipping")

        if not os.path.exists(comments_path) or os.path.getsize(comments_path) == 0:
            download_type(sub, "comments", comments_path)
        else:
            print(f"  comments file exists, skipping")

        print()

    print("All downloads complete.")


if __name__ == "__main__":
    main()
