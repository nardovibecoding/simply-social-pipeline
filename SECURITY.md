# Security Policy

## Supported Versions

The `main` branch is the supported public template.

## Reporting A Vulnerability

Open a private GitHub security advisory for vulnerabilities. Do not publish
drafts, account identifiers, API keys, cookies, OAuth files, local paths, logs,
or metrics in public issues.

## Local Data

Keep real drafts, queues, generated metrics, cookies, and notification webhook
URLs out of git. Use `.env.example` for fake placeholders only.

Posting is opt-in: scripts should dry-run unless an explicit confirmation flag
is provided.
