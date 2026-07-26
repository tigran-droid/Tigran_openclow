---
name: ai-content-briefing
description: Collects AI news, archives the raw material to GitHub, then writes 3 LinkedIn post ideas for an AI-transformation consulting business. Rules live in GitHub.
---

# AI Content Briefing

Trigger when the user asks for "today's briefing", "AI news", or "LinkedIn ideas".

## Step 1 — Load the current rules (always fetch fresh)
Fetch these from GitHub first, always the latest version:
- Filtering rules: https://raw.githubusercontent.com/tigran-droid/Tigran_openclow/main/what_is_important.md
- Writing style: https://raw.githubusercontent.com/tigran-droid/Tigran_openclow/main/how_to_write.md
- Sources list: https://raw.githubusercontent.com/tigran-droid/Tigran_openclow/main/sources.md

## Step 2 — Collect raw material
From every source in sources.md:
- RSS feeds: fetch the 5 newest items (title, link, and text).
- YouTube / podcasts: if any are listed, get the transcript text if you can.
Gather all of it as raw text.

## Step 3 — Archive the raw material to GitHub (do this BEFORE summarizing)
Create a new file in the repo named raw/<TODAY>.md (example: raw/2026-07-26.md).
Put ALL the raw collected text inside it.
Use the GitHub API:
- PUT https://api.github.com/repos/tigran-droid/Tigran_openclow/contents/raw/<TODAY>.md
- Header: Authorization: Bearer <value of the GITHUB_TOKEN environment variable>
- Header: Accept: application/vnd.github+json
- JSON body: { "message": "raw archive <TODAY>", "content": "<all the raw text, base64-encoded>" }
Never print the token. If the file already exists, add the time to the filename.

## Step 4 — Filter
Using what_is_important.md, keep only items that matter. Skip the rest.

## Step 5 — Write
Using how_to_write.md, write exactly 3 LinkedIn post ideas from the best items. Number them 1, 2, 3, each with a source link.

## Step 6 — Reply
Send the 3 ideas to the user, and include the link to today's raw archive file.
