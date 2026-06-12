# Source Packets

Use source packets to separate public context gathering from draft writing and
posting. A packet is evidence for the draft queue, not a publishing command.

## When To Use

- The user asks for a post based on public X/Twitter discussion.
- The user wants to turn searched tweets, replies, or monitor summaries into
  a draft angle.
- The user provides a reviewed export from TweetClaw, an X/Twitter MCP tool, or
  another approved collector.

Do not create new monitors, webhooks, direct messages, replies, posts, follows,
media uploads, or giveaway draws while building a packet. Those are separate
account actions and need fresh approval outside this source step.

## Packet Shape

Save packets under:

```text
$CONTENT_PIPELINE_HOME/sources/x-social/YYYY-MM-DD-topic.md
```

Use this structure:

```markdown
# X/Twitter Source Packet: <topic>

Collected: <ISO timestamp>
Collector: <tool name and version>
Scope: <search query, account, monitor, or webhook summary>
User approval: <what the user approved>

## Useful Evidence

- <tweet URL or public account URL> - <fact, quote summary, metric, or angle>
- <tweet URL or public account URL> - <fact, quote summary, metric, or angle>

## Draft Angles

- <short angle that could become a post>
- <short angle that could become a thread>

## Exclusions

- <private data removed>
- <account actions not approved>
```

## TweetClaw Input

[TweetClaw](https://github.com/Xquik-dev/tweetclaw) is an optional OpenClaw
plugin, published as
[`@xquik/tweetclaw`](https://registry.npmjs.org/@xquik%2ftweetclaw), for
collecting approved public X/Twitter context before this skill drafts. It can
help with jobs such as scrape tweets, search tweets, search tweet replies,
follower export summaries, user lookup, media download metadata, existing
monitor summaries, and webhook summaries.

Install from npm when OpenClaw is the agent host:

```bash
openclaw plugins install @xquik/tweetclaw@1.6.31
```

Keep the packet as the boundary:

- TweetClaw gathers reviewed public evidence.
- `x-tweet` decides the draft angle, voice, and queue placement.
- `scripts/post_tweet.py` still dry-runs unless `--confirm-post` is passed.
- The user must approve final text before any post, reply, or media action.

## Drafting Checklist

Before drafting:

- Remove private identifiers, keys, paths, logs, screenshots, and internal notes.
- Prefer public URLs and short evidence summaries over copied full text.
- Keep claims sourced to the packet.
- Treat engagement counts as context, not proof.
- Save the draft to the queue before asking about publishing.
