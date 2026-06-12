# simply-social-pipeline

A local content-capture and draft pipeline for developer storytelling.

This repo gives you a small MCP-compatible content server, a draft queue, a text
humanizer, and optional social posting adapters. It is a public template, not a
mirror of any private content workflow.

## Quickstart

```bash
gh repo clone nardovibecoding/simply-social-pipeline
cd simply-social-pipeline
bash install.sh
```

Requirements:

- Python 3.10+
- `pip`
- macOS or Linux

The installer uses `~/simply-social-pipeline` and stores drafts under
`~/content-pipeline` by default. Override them with:

```bash
INSTALL_DIR="$HOME/tools/simply-social-pipeline" \
CONTENT_PIPELINE_HOME="$HOME/content-pipeline" \
bash install.sh
```

## What You Get

| Component | Purpose |
|---|---|
| `mcp/` | local content capture, queue, checkpoint, reminder, and review tools |
| `skills/content-humanizer/` | local text review and rewrite prompts |
| `skills/x-tweet/` | optional social draft workflow with source packets and a manual posting gate |
| `install.sh` | local installer with configurable paths |

## Safe Defaults

- Drafts are written to `CONTENT_PIPELINE_HOME`, defaulting to
  `~/content-pipeline`.
- Posting scripts do not post unless you pass an explicit confirmation flag.
- Notification hooks are optional and use fake `.env.example` values.
- Real drafts, logs, cookies, OAuth files, metrics, and API keys stay out of
  git.

## Common Commands

```bash
# install locally
bash install.sh

# run content functions directly
python3 - <<'PY'
from mcp.lib import content_capture, content_queue
print(content_capture("Found a simpler API boundary", "insight"))
print(content_queue("add", "Tiny draft goes here", "normal"))
PY

# score a draft for common AI-writing tells
printf "This is a direct draft with concrete detail.\n" > /tmp/draft.txt
python3 skills/content-humanizer/scripts/humanizer_scorer.py /tmp/draft.txt

# prepare a social post without publishing
python3 skills/x-tweet/scripts/post_tweet.py "Draft text" --dry-run
```

## Configuration

Copy `.env.example` and edit locally. Keep real values out of git.

```env
CONTENT_PIPELINE_HOME=~/content-pipeline
SOCIAL_USERNAME=example_user
X_API_KEY=replace_me
X_API_SECRET=replace_me
X_ACCESS_TOKEN=replace_me
X_ACCESS_TOKEN_SECRET=replace_me
CONTENT_NOTIFY_WEBHOOK_URL=
```

## Optional Posting Adapter

`skills/x-tweet/scripts/post_tweet.py` can publish through X API v2 only after
you provide credentials and pass `--confirm-post`.

For source material, see
[`skills/x-tweet/references/source-packets.md`](skills/x-tweet/references/source-packets.md)
for a reviewed packet shape that can bring public X/Twitter context into the
draft queue without changing the posting gate.

```bash
python3 skills/x-tweet/scripts/post_tweet.py "hello from the draft queue" --dry-run
python3 skills/x-tweet/scripts/post_tweet.py "approved post text" --confirm-post
```

Use `--no-alert` to skip the optional notification webhook.

## Public Template Boundary

This public template intentionally omits:

- private assistant transcript paths
- private content drafts and queues
- real account analytics history
- cookies, OAuth files, and session state
- live Telegram bot or chat identifiers
- unattended social posting

## Review Policy

This is a solo-maintainer public template. Security-sensitive changes should be
reviewed before release.

## License

AGPL-3.0-or-later
