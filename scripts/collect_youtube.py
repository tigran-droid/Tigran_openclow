#!/usr/bin/env python3
"""
Deterministic YouTube collector for the content agent.

It does the MECHANICAL work reliably so the AI agent does not have to:
  - reads sources.md from GitHub (channels + one-time YouTube links)
  - for each channel, finds videos published in the last N hours (via the
    channel RSS feed, which has real dates)
  - for each one-time YouTube link, always includes it (no dedup for now)
  - fetches every transcript through the Supadata API
  - prints one clean markdown block per video (title, url, published, transcript)

The agent runs this, then filters/writes from the output.

Usage:  python3 collect_youtube.py            (default window 26 hours)
        WINDOW_HOURS=48 python3 collect_youtube.py
"""

import os, re, sys, json, urllib.request, urllib.parse
from datetime import datetime, timezone, timedelta

SUPADATA_KEY = os.environ.get("SUPADATA_API_KEY", "").strip()
REPO_RAW = "https://raw.githubusercontent.com/tigran-droid/Tigran_openclow/main"
WINDOW_HOURS = int(os.environ.get("WINDOW_HOURS", "26"))
UA = {"User-Agent": "Mozilla/5.0 (content-agent collector)"}


def fetch(url, headers=None, timeout=45):
    req = urllib.request.Request(url, headers={**UA, **(headers or {})})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def log(msg):
    print(msg, file=sys.stderr)


def get_sources_md():
    return fetch(f"{REPO_RAW}/sources.md?nocache={int(datetime.now().timestamp())}")


def parse_sections(md):
    sections = {"channels": [], "onetime": []}
    cur = None
    for line in md.splitlines():
        l = line.strip()
        if l.startswith("## 2"): cur = "channels"; continue
        if l.startswith("## 4"): cur = "onetime"; continue
        if l.startswith("## 1") or l.startswith("## 3"): cur = None; continue
        if l.startswith("### Already done"): cur = None; continue
        m = re.match(r"^-\s*(https?://\S+)", l)
        if m and cur:
            sections[cur].append(m.group(1))
    return sections


def channel_id(url):
    try:
        html = fetch(url.rstrip("/") + "/videos")
    except Exception as e:
        log(f"  ! could not load channel page {url}: {e}")
        return None
    for pat in (r"channel_id=(UC[A-Za-z0-9_-]+)", r'"channelId":"(UC[A-Za-z0-9_-]+)"',
                r"externalId\"?:\"?(UC[A-Za-z0-9_-]+)"):
        m = re.search(pat, html)
        if m:
            return m.group(1)
    return None


def channel_recent(url):
    cid = channel_id(url)
    if not cid:
        log(f"  ! no channel id for {url}")
        return []
    feed = fetch(f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}")
    out = []
    for entry in re.findall(r"<entry>(.*?)</entry>", feed, re.S):
        vid = re.search(r"<yt:videoId>([^<]+)", entry)
        title = re.search(r"<title>([^<]+)", entry)
        pub = re.search(r"<published>([^<]+)", entry)
        if vid and pub:
            out.append((vid.group(1),
                        (title.group(1) if title else "").strip(),
                        pub.group(1).strip()))
    return out


def within_window(iso):
    try:
        dt = datetime.fromisoformat(iso.replace("Z", "+00:00"))
        return (datetime.now(timezone.utc) - dt) <= timedelta(hours=WINDOW_HOURS)
    except Exception:
        return False


def transcript(video_url):
    if not SUPADATA_KEY:
        return None, "SUPADATA_API_KEY is not set"
    api = ("https://api.supadata.ai/v1/youtube/transcript?url="
           + urllib.parse.quote(video_url, safe="") + "&text=true")
    try:
        data = json.loads(fetch(api, headers={"x-api-key": SUPADATA_KEY}))
    except Exception as e:
        return None, f"api error: {e}"
    if isinstance(data, dict) and data.get("content"):
        return data["content"], None
    err = (data or {}).get("error") if isinstance(data, dict) else None
    return None, err or "no transcript content returned"


def emit(title, url, published, source_kind):
    text, err = transcript(url)
    print(f"\n## {title or url}")
    print(f"Source: {url}")
    print(f"Published: {published}")
    print(f"Type: {source_kind}")
    if text:
        print(f"\n{text}\n")
        log(f"  + transcript OK ({len(text.split())} words): {title[:50]}")
        return True
    else:
        print(f"\n[NO TRANSCRIPT AVAILABLE — {err}]\n")
        log(f"  - no transcript ({err}): {title[:50]}")
        return False


def main():
    log(f"collector: window={WINDOW_HOURS}h  key={'set' if SUPADATA_KEY else 'MISSING'}")
    try:
        secs = parse_sections(get_sources_md())
    except Exception as e:
        log(f"FATAL: could not read sources.md: {e}")
        sys.exit(1)

    print(f"# YouTube raw material — collected {datetime.now(timezone.utc).isoformat()}")
    got = 0

    log(f"channels: {len(secs['channels'])}")
    for ch in secs["channels"]:
        log(f"channel {ch}")
        for vid, title, pub in channel_recent(ch):
            if within_window(pub):
                if emit(title, f"https://www.youtube.com/watch?v={vid}", pub, "channel video (last %dh)" % WINDOW_HOURS):
                    got += 1

    log(f"one-time: {len(secs['onetime'])}")
    for link in secs["onetime"]:
        if "youtube.com" in link or "youtu.be" in link:
            log(f"one-time {link}")
            if emit("one-time request", link, "n/a", "one-time YouTube request"):
                got += 1

    print(f"\n<!-- collector done: {got} transcript(s) collected -->")
    log(f"DONE: {got} transcript(s)")


if __name__ == "__main__":
    main()
