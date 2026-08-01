#!/usr/bin/env python3
"""
Deterministic X/Twitter collector for the content agent.

Mirrors collect_youtube.py: it does the MECHANICAL work reliably so the AI
agent does not have to.

  - reads sources.md from GitHub, section "5. X / Twitter accounts"
  - for each account, fetches their most recent posts
  - keeps only posts from the last N hours
  - prints one clean markdown block per post (author, url, date, text)

The agent runs this, then filters/writes from the output.

Provider is pluggable: today twitterapi.io (cheap, free trial credit).
Switching to the official X API later means changing only fetch_user_posts().

Usage:  python3 collect_x.py
        WINDOW_HOURS=48 python3 collect_x.py
"""

import os, re, sys, json, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

API_KEY = os.environ.get("TWITTERAPI_IO_KEY", "").strip()
REPO_RAW = "https://raw.githubusercontent.com/tigran-droid/Tigran_openclow/main"
WINDOW_HOURS = int(os.environ.get("WINDOW_HOURS", "26"))
MAX_PER_ACCOUNT = int(os.environ.get("MAX_PER_ACCOUNT", "20"))
UA = {"User-Agent": "Mozilla/5.0 (content-agent collector)"}


def fetch(url, headers=None, timeout=45):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def log(msg):
    print(msg, file=sys.stderr)


def get_sources_md():
    return fetch(f"{REPO_RAW}/sources.md?nocache={int(datetime.now().timestamp())}")


def parse_accounts(md):
    """Read the '## 5.' section and return a list of bare handles."""
    accounts, in_section = [], False
    for line in md.splitlines():
        l = line.strip()
        if l.startswith("## 5"):
            in_section = True
            continue
        if in_section and l.startswith("## "):
            break
        if not in_section:
            continue
        m = re.match(r"^-\s*(\S+)", l)
        if not m:
            continue
        raw = m.group(1)
        # accept: @handle, handle, x.com/handle, twitter.com/handle, full urls
        h = raw.strip().rstrip("/")
        h = re.sub(r"^https?://(www\.)?(x|twitter)\.com/", "", h)
        h = h.split("?")[0].split("/")[0]
        h = h.lstrip("@")
        if h and not h.startswith("<!--"):
            accounts.append(h)
    return accounts


def parse_created(s):
    """twitterapi.io returns e.g. 'Tue Dec 10 07:00:30 +0000 2024'."""
    for fmt in ("%a %b %d %H:%M:%S %z %Y", "%Y-%m-%dT%H:%M:%S%z", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            dt = datetime.strptime(s, fmt)
            return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
        except Exception:
            continue
    return None


def within_window(dt):
    return dt is not None and (datetime.now(timezone.utc) - dt) <= timedelta(hours=WINDOW_HOURS)


def fetch_user_posts(handle):
    """Provider-specific. Returns list of dicts: text, url, created (datetime)."""
    if not API_KEY:
        log("  ! TWITTERAPI_IO_KEY is not set")
        return []
    url = ("https://api.twitterapi.io/twitter/user/last_tweets?userName="
           + urllib.parse.quote(handle))
    try:
        data = json.loads(fetch(url, headers={"X-API-Key": API_KEY}))
    except Exception as e:
        log(f"  ! api error for @{handle}: {e}")
        return []

    # tweets may sit at top level or under "data"
    tweets = data.get("tweets")
    if tweets is None and isinstance(data.get("data"), dict):
        tweets = data["data"].get("tweets")
    if tweets is None:
        log(f"  ! unexpected response shape for @{handle}: {list(data)[:5]}")
        return []

    out = []
    for t in tweets[:MAX_PER_ACCOUNT]:
        created = parse_created(t.get("createdAt", "") or "")
        out.append({
            "text": (t.get("text") or "").strip(),
            "url": t.get("url") or f"https://x.com/{handle}/status/{t.get('id','')}",
            "created": created,
        })
    return out


def main():
    log(f"x collector: window={WINDOW_HOURS}h  key={'set' if API_KEY else 'MISSING'}")
    try:
        accounts = parse_accounts(get_sources_md())
    except Exception as e:
        log(f"FATAL: could not read sources.md: {e}")
        sys.exit(1)

    print(f"# X / Twitter raw material — collected {datetime.now(timezone.utc).isoformat()}")
    log(f"accounts: {len(accounts)} -> {accounts}")

    total = 0
    for handle in accounts:
        log(f"@{handle}")
        kept = 0
        for p in fetch_user_posts(handle):
            if not within_window(p["created"]):
                continue
            if not p["text"]:
                continue
            print(f"\n## @{handle} — post")
            print(f"Source: {p['url']}")
            print(f"Published: {p['created'].isoformat()}")
            print(f"Type: X post (last {WINDOW_HOURS}h)")
            print(f"\n{p['text']}\n")
            kept += 1
        log(f"  + {kept} post(s) in window")
        total += kept

    print(f"\n<!-- x collector done: {total} post(s) collected -->")
    log(f"DONE: {total} post(s)")


if __name__ == "__main__":
    main()
