#!/usr/bin/env python3
"""
Turn text into a Telegram voice note.

Reads the text on stdin, speaks it with Piper (local, free, unlimited),
converts to Opus so Telegram shows a real voice note (tap-and-listen, not a
file attachment), and sends it.

Usage:
  echo "some text" | python3 speak.py --to 1931839672 --caption "Daily news"
  python3 speak.py --to 1931839672 --caption "..." --file /path/to/text.txt

Switching to a more natural paid voice later means changing only synth().
"""

import os, re, sys, subprocess, tempfile, argparse, uuid

VOICE = os.environ.get("PIPER_VOICE", "/root/piper-voices/en_US-lessac-medium.onnx")
MEDIA_DIR = "/root/.openclaw/workspace/media"   # openclaw only sends media from here
MAX_CHARS = int(os.environ.get("TTS_MAX_CHARS", "6000"))


def clean_for_speech(text: str) -> str:
    """Strip anything that sounds wrong when read aloud."""
    t = text
    t = re.sub(r"\[\d+/\d+\][^\n]*\n", "", t)      # [2/7] headers
    t = re.sub(r"^[─—\-=_]{3,}$", "", t, flags=re.M)  # divider lines
    t = re.sub(r"https?://\S+", "", t)              # urls
    t = re.sub(r"[*_`#>|]", " ", t)                 # markdown marks
    t = re.sub(r"[\U0001F300-\U0001FAFF☀-➿️]", "", t)  # emoji
    t = re.sub(r"[ \t]+", " ", t)
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()[:MAX_CHARS]


def synth(text: str, wav_path: str) -> None:
    """Provider-specific. Piper today; swap this for a paid TTS later."""
    subprocess.run(["piper", "-m", VOICE, "-f", wav_path],
                   input=text, text=True, check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def to_voice_note(wav_path: str, ogg_path: str) -> None:
    subprocess.run(["ffmpeg", "-y", "-i", wav_path,
                    "-c:a", "libopus", "-b:a", "32k", "-ar", "48000", "-ac", "1",
                    ogg_path], check=True,
                   stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def send(ogg_path: str, target: str, caption: str) -> int:
    cmd = ["openclaw", "message", "send", "--channel", "telegram",
           "--target", target, "--media", ogg_path]
    if caption:
        cmd += ["-m", caption]
    r = subprocess.run(cmd, capture_output=True, text=True)
    print(r.stdout.strip() or r.stderr.strip(), file=sys.stderr)
    return r.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--to", required=True, help="Telegram chat id")
    ap.add_argument("--caption", default="", help="short text shown with the voice note")
    ap.add_argument("--file", help="read text from a file instead of stdin")
    a = ap.parse_args()

    raw = open(a.file, encoding="utf-8").read() if a.file else sys.stdin.read()
    text = clean_for_speech(raw)
    if not text:
        print("nothing to speak", file=sys.stderr)
        return 1

    os.makedirs(MEDIA_DIR, exist_ok=True)
    stem = uuid.uuid4().hex[:8]
    wav = os.path.join(tempfile.gettempdir(), f"tts-{stem}.wav")
    ogg = os.path.join(MEDIA_DIR, f"voice-{stem}.ogg")

    try:
        synth(text, wav)
        to_voice_note(wav, ogg)
        rc = send(ogg, a.to, a.caption)
    finally:
        for p in (wav,):
            try: os.remove(p)
            except OSError: pass
        # keep only the 20 newest voice notes
        try:
            files = sorted((os.path.join(MEDIA_DIR, f) for f in os.listdir(MEDIA_DIR)
                            if f.startswith("voice-")), key=os.path.getmtime, reverse=True)
            for old in files[20:]:
                os.remove(old)
        except OSError:
            pass
    return rc


if __name__ == "__main__":
    sys.exit(main())
