#!/usr/bin/env bash
# simply-social-pipeline local installer.
set -euo pipefail

REPO_URL="${REPO_URL:-https://github.com/nardovibecoding/simply-social-pipeline.git}"
INSTALL_DIR="${INSTALL_DIR:-$HOME/simply-social-pipeline}"
CONTENT_PIPELINE_HOME="${CONTENT_PIPELINE_HOME:-$HOME/content-pipeline}"
ASSISTANT_SETTINGS="${ASSISTANT_SETTINGS:-}"

echo "==> simply-social-pipeline install"
echo "    install dir: $INSTALL_DIR"
echo "    draft home:  $CONTENT_PIPELINE_HOME"

if ! command -v python3 >/dev/null 2>&1; then
  echo "python3 is required" >&2
  exit 1
fi

if [ -d "$INSTALL_DIR/.git" ]; then
  git -C "$INSTALL_DIR" pull --ff-only
elif [ -d "$INSTALL_DIR" ]; then
  echo "$INSTALL_DIR exists but is not a git repo. Set INSTALL_DIR or remove it." >&2
  exit 1
else
  git clone "$REPO_URL" "$INSTALL_DIR"
fi

mkdir -p "$CONTENT_PIPELINE_HOME"/{drafts,logs,metrics}

python3 -m pip install --quiet --user mcp >/dev/null 2>&1 || {
  echo "warning: could not install mcp automatically; run: python3 -m pip install --user mcp" >&2
}

if [ -n "$ASSISTANT_SETTINGS" ]; then
  python3 - "$ASSISTANT_SETTINGS" "$INSTALL_DIR" <<'PY'
import json
import sys
from pathlib import Path

settings_path = Path(sys.argv[1]).expanduser()
install_dir = Path(sys.argv[2]).expanduser()
settings_path.parent.mkdir(parents=True, exist_ok=True)

if settings_path.exists():
    settings = json.loads(settings_path.read_text())
else:
    settings = {}

mcp = settings.setdefault("mcpServers", {})
mcp["content-pipeline"] = {
    "command": "python3",
    "args": [str(install_dir / "mcp" / "server.py")],
}
settings_path.write_text(json.dumps(settings, indent=2) + "\n")
print(f"configured MCP server in {settings_path}")
PY
else
  echo "ASSISTANT_SETTINGS not set; skipped assistant config mutation."
fi

echo "==> install complete"
echo "Run with: CONTENT_PIPELINE_HOME=\"$CONTENT_PIPELINE_HOME\" python3 \"$INSTALL_DIR/mcp/server.py\""
