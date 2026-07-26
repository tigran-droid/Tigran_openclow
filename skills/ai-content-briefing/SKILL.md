---
name: ai-content-briefing
description: Reads AI news and writes 3 LinkedIn post ideas for an AI-transformation consulting business, using rules stored in GitHub.
---

# AI Content Briefing

Trigger this skill when the user asks for "today's briefing", "AI news",
or "LinkedIn ideas".

## Step 1 — Load the current rules (always fetch fresh, do not cache)

Fetch these three files from GitHub before doing anything else. They may
change at any time — always use the latest version, never rely on memory
of a previous run:

- Filtering rules: https://raw.githubusercontent.com/tigran-droid/Tigran_openclow/main/what_is_important.md
- Writing style: https://raw.githubusercontent.com/tigran-droid/Tigran_openclow/main/how_to_write.md
- Sources list: https://raw.githubusercontent.com/tigran-droid/Tigran_openclow/main/sources.md

## Step 2 — Collect

Fetch the newest items from every RSS feed listed in sources.md. Take the
5 newest items per feed.

## Step 3 — Filter

Using the rules in what_is_important.md, judge each item. Keep only the
ones that genuinely matter. Skip the rest.

## Step 4 — Write

Using the style in how_to_write.md, write exactly 3 LinkedIn post ideas
from the most important remaining items. Number them 1, 2, 3, each with
a source link.

## Step 5 — Reply

Send the 3 ideas back to the user in the chat, clearly numbered.
