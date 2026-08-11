<!-- ────────────────────────────────────────────────────────────
     Hi Chris 👋   (sources.md)

     WHAT THIS FILE DOES
     This is your source list — everything the agent follows.
     Add or remove links below. Every line must start with a dash and a space.
     ──────────────────────────────────────────────────────────── -->

## ✏️ Your quick changes

Write small changes here in plain English. You do not need to find the right
place in the file below — just write what you want and the agent will apply it.
These notes take priority over everything else in this file.

Examples of what you could write:
  e.g. "ignore anything about crypto"
  e.g. "check the YouTube channels twice a day"
  e.g. "pause the X accounts for now"

Write yours below this line (delete anything you no longer want):

<!-- START OF YOUR NOTES -->

<!-- END OF YOUR NOTES -->

---

# Sources — Chrisy's control panel

This is the list the agent follows every day.
Just paste a NORMAL link (the website, channel or show address). You never need
to find an RSS feed — the agent finds it for you.

To pause a source: put a # in front of the line.

---

## 1. Blogs & news
Paste the normal website or blog address.

These are starting suggestions — delete any you do not want, and add Chrisy's
own. The system needs enough material every day to find real themes; with only
one or two sources the content ends up being about a single article.

- https://www.oneusefulthing.org
- https://www.technologyreview.com/topic/artificial-intelligence/
- https://www.anthropic.com/news
- https://openai.com/news/
- https://www.ben-evans.com/benedictevans


---

## 2. YouTube channels (checked daily for new videos)
Paste the channel link (a channel, not a single video).

<!-- example: - https://www.youtube.com/@channelname -->
- https://www.youtube.com/@mreflow
- https://www.youtube.com/@futurepedia_io
- https://www.youtube.com/@nateherk
- https://www.youtube.com/@AIDailyBrief
---

## 3. Podcasts
Two ways to add a podcast — both work:

BEST: paste the podcast's RSS feed URL directly if you have it. Faster and more
reliable, and many feeds include the episode transcript, which we use directly.

OR: paste any normal podcast link (Spotify, Apple Podcasts, or the show's own
website) and the agent will find the feed behind it.

IMPORTANT: start each line with "- " or the agent will not see it.
Also check the show is not already in section 2 as a YouTube channel — YouTube
gives us the full transcript, a podcast feed usually only gives show notes.

<!-- example (RSS, preferred): - https://feeds.megaphone.fm/showname -->
<!-- example (normal link):    - https://podcasts.apple.com/us/podcast/name/id123456789 -->

<!-- NOTE: The AI Daily Brief is already followed on YouTube in section 2,
     where we get the full transcript. Its podcast feed only carries show
     notes, so adding it here would duplicate the same show with less content.
     Uncomment the line below only if you want it anyway.
- https://anchor.fm/s/f7cac464/podcast/rss
-->


---

## 5. X / Twitter accounts (checked daily for new posts)
Paste the person's X profile — any of these forms works:
@username, username, or https://x.com/username

The agent checks each account every day and takes their posts from the last
26 hours. Their posts land in the same daily raw archive as the YouTube
transcripts.

<!-- example: - @karpathy -->
<!-- example: - https://x.com/sama -->
- @karpathy
- @sama
- @emollick
- @EugenioFierro3


---

## 4. One-time requests (single links, processed once)
Use this when you want ONE specific video, article or episode included in
today's summary — not a whole channel, just this one link.

Paste it below. It does NOT need to be recent — the agent will process it
regardless of publish date, unlike sections 1-3 which only look at the last
24 hours. On the next run, the agent reads its transcript / full text, folds
it into today's briefing and content, then moves the line down to
"Already done" so it is never processed twice.


### Already done (the agent moves finished items here — do not edit)
- 2026-07-31 | https://www.youtube.com/watch?v=jYHQRP28hGM
