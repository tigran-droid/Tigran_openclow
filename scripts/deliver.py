#!/usr/bin/env python3
"""
Deliver the finished daily brief to Telegram.

The agent writes the brief as plain text files, one per message, then runs this
script once. The script — not the agent — decides what gets sent, in what order,
and where the voice notes go. That is deliberate: asking the agent in prose to
remember a final step has never worked, and voice notes were silently skipped on
every run because of it.

  python3 deliver.py --to 1931839672 --dir /root/brief

Expected files in --dir (plain text, exactly as Chrisy should read them,
header line and divider included):

  01-briefing.txt      02-news.txt          03-post1.txt
  04-post2.txt         05-post3.txt         06-article.txt
  07-blog-ideas.txt

  voice-news.txt       spoken after 02-news.txt
  voice-posts.txt      spoken after 05-post3.txt

Text messages are required — a missing one is an error. Voice files are optional:
if one is absent it is skipped, and if speaking fails the text delivery still
counts as a success, because the text matters more.
"""

import os, sys, glob, argparse, subprocess

SPEAK = "/root/speak.py"
TELEGRAM_LIMIT = 4096
CHUNK_TARGET = 3800          # leave room for the "(continued)" marker

# Which voice file follows which message, and the caption Chrisy sees.
VOICE_AFTER = {
    "02-news.txt":  ("voice-news.txt",  "🎧 Daily news — listen"),
    "05-post3.txt": ("voice-posts.txt", "🎧 The three post ideas — listen"),
}

REQUIRED = ["01-briefing.txt", "02-news.txt", "03-post1.txt", "04-post2.txt",
            "05-post3.txt", "06-article.txt", "07-blog-ideas.txt"]


def split_for_telegram(text):
    """Telegram cuts anything over 4096 chars at a random point, mid-sentence.

    Split on paragraph breaks instead, so each piece ends where the writing
    ends. Only the article is ever long enough to need this.
    """
    if len(text) <= TELEGRAM_LIMIT:
        return [text]

    chunks, current = [], ""
    for para in text.split("\n\n"):
        candidate = f"{current}\n\n{para}" if current else para
        if len(candidate) <= CHUNK_TARGET:
            current = candidate
        else:
            if current:
                chunks.append(current)
            # a single paragraph over the limit still has to be broken somewhere
            while len(para) > CHUNK_TARGET:
                cut = para.rfind(" ", 0, CHUNK_TARGET)
                cut = cut if cut > 0 else CHUNK_TARGET
                chunks.append(para[:cut])
                para = para[cut:].lstrip()
            current = para
    if current:
        chunks.append(current)

    return [c if i == 0 else f"(continued)\n\n{c}" for i, c in enumerate(chunks)]


def send_text(text, target):
    r = subprocess.run(
        ["openclaw", "message", "send", "--channel", "telegram",
         "--target", target, "-m", text],
        capture_output=True, text=True)
    if r.returncode != 0:
        print(f"    FAILED: {(r.stderr or r.stdout).strip()}", file=sys.stderr)
    return r.returncode == 0


def send_voice(path, target, caption):
    with open(path, encoding="utf-8") as f:
        text = f.read().strip()
    if not text:
        print(f"    skipped {os.path.basename(path)} — empty", file=sys.stderr)
        return False
    r = subprocess.run(["python3", SPEAK, "--to", target, "--caption", caption],
                       input=text, text=True, capture_output=True)
    if r.returncode != 0:
        print(f"    voice note FAILED: {(r.stderr or r.stdout).strip()}", file=sys.stderr)
    return r.returncode == 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", required=True, help="Telegram chat id")
    ap.add_argument("--dir", default="/root/brief", help="folder holding the brief files")
    a = ap.parse_args()

    missing = [n for n in REQUIRED if not os.path.isfile(os.path.join(a.dir, n))]
    if missing:
        print(f"Nothing sent. Missing: {', '.join(missing)}", file=sys.stderr)
        return 1

    parts = sorted(glob.glob(os.path.join(a.dir, "[0-9][0-9]-*.txt")))
    sent_text = sent_voice = failed = 0

    for path in parts:
        name = os.path.basename(path)
        with open(path, encoding="utf-8") as f:
            body = f.read().strip()
        if not body:
            print(f"  {name}: empty, skipped", file=sys.stderr)
            continue

        for chunk in split_for_telegram(body):
            if send_text(chunk, a.to):
                sent_text += 1
            else:
                failed += 1

        voice = VOICE_AFTER.get(name)
        if voice:
            vpath = os.path.join(a.dir, voice[0])
            if os.path.isfile(vpath) and send_voice(vpath, a.to, voice[1]):
                sent_voice += 1

    summary = f"Sent {sent_text} text messages and {sent_voice} voice notes."
    if failed:
        summary += f" {failed} message(s) failed to send."
    print(summary)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
