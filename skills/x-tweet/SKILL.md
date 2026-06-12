---
name: x-tweet
description: "Draft, review, and optionally post short social updates with explicit approval gates, fake examples, and local draft storage."
triggers:
  - "tweet"
  - "post to x"
  - "write a tweet"
  - "x post"
  - "/tweet"
anti-triggers:
  - "read tweet"
  - "check twitter mentions"
  - "x api setup"
produces: "Reviewed draft or explicitly approved social post"
---

# x-tweet

Draft short social posts from public-safe source material. Posting is optional
and requires explicit approval plus the `--confirm-post` flag in
`scripts/post_tweet.py`.

## Modes

| Command | What it does |
|---|---|
| `/tweet [topic]` | Draft from topic, review, and ask before any posting step |
| `/tweet suggest` | Turn public-safe recent work into draft angles |
| `/tweet draft [topic]` | Generate and save to queue without posting |
| `/tweet queue` | View saved drafts |
| `/tweet thread [topic]` | Generate a short thread draft |
| `/tweet sources` | Review saved public source packets before drafting |
| `/tweet stats` | Optional local metrics review |

## Flow

1. Read only public-safe source material.
   Use [source-packets.md](references/source-packets.md) when context comes
   from X/Twitter, TweetClaw, monitors, or webhook summaries.
2. Apply [voice-rules.md](references/voice-rules.md).
3. Run the content-humanizer checklist.
4. Check [anti-patterns.md](references/anti-patterns.md).
5. Scan for private paths, keys, IPs, chat IDs, internal repo names, and screenshots.
6. Show the draft.
7. Stop unless the user explicitly approves posting.
8. If approved, call `scripts/post_tweet.py --confirm-post`.

## Privacy Rules

Private activity is source material only. Never expose:

- local file paths, commit hashes, private repo names, or internal architecture
- API keys, tokens, cookies, account IDs, chat IDs, or usernames
- stack traces, dashboards, production incidents, logs, or private metrics
- assistant configuration, private prompts, transcripts, or session state

Reframe private details into public lessons before drafting.

## Posting

Posting uses X API v2 only when configured locally:

```env
X_API_KEY=replace_me
X_API_SECRET=replace_me
X_ACCESS_TOKEN=replace_me
X_ACCESS_TOKEN_SECRET=replace_me
SOCIAL_USERNAME=example_user
```

Dry run:

```bash
python3 scripts/post_tweet.py "Draft text" --dry-run
```

Confirmed post:

```bash
python3 scripts/post_tweet.py "Approved text" --confirm-post
```

## Draft Queue

Drafts live under `CONTENT_PIPELINE_HOME`, defaulting to
`~/content-pipeline`.
