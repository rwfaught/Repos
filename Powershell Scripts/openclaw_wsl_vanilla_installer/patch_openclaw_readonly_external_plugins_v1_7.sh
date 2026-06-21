#!/usr/bin/env bash
# patch_openclaw_readonly_external_plugins_v1_7.sh
#
# OpenClaw compatibility patch for OpenClaw 2026.5.28 channel list status.
# FIX_v1_7_62: include loadable external channel plugins, such as Discord, in
# the read-only channels list plugin loop without writing channel config.

set -Eeuo pipefail

LOG_DIR="${LOG_DIR:-}"
OPENCLAW_ROOT="${OPENCLAW_ROOT:-/usr/lib/node_modules/openclaw}"

usage() {
  cat <<'EOF'
Usage:
  bash patch_openclaw_readonly_external_plugins_v1_7.sh [--log-dir DIR] [--openclaw-root DIR]

Options:
  --log-dir DIR        Directory for proof output. Default: current directory.
  --openclaw-root DIR  Installed OpenClaw package root. Default: /usr/lib/node_modules/openclaw.
  --help              Show this help.

This script patches installed OpenClaw dist files only. It does not read, write,
or print Discord token values and does not write OpenClaw channel config.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --log-dir) LOG_DIR="${2:-}"; shift 2 ;;
    --openclaw-root) OPENCLAW_ROOT="${2:-}"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) printf 'Unknown option: %s\n' "$1" >&2; usage >&2; exit 2 ;;
  esac
done

if [[ -z "$LOG_DIR" ]]; then
  LOG_DIR="$(pwd)"
fi
mkdir -p "$LOG_DIR"

if [[ "${OPENCLAW_OPENCLAW_PATCH_ELEVATED:-0}" != "1" && -d "$OPENCLAW_ROOT" && ! -w "$OPENCLAW_ROOT" ]]; then
  if ! command -v sudo >/dev/null 2>&1; then
    printf 'PATCH_RESULT=failed\nERROR_REASON=openclaw-root-not-writable-and-sudo-missing\n' >&2
    exit 1
  fi
  exec sudo -n env \
    HOME="$HOME" \
    PATH="$PATH" \
    LOG_DIR="$LOG_DIR" \
    OPENCLAW_ROOT="$OPENCLAW_ROOT" \
    OPENCLAW_OPENCLAW_PATCH_ELEVATED=1 \
    bash "$0" --log-dir "$LOG_DIR" --openclaw-root "$OPENCLAW_ROOT"
fi

python3 - "$OPENCLAW_ROOT" "$LOG_DIR" <<'PY'
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

openclaw_root = Path(sys.argv[1])
log_dir = Path(sys.argv[2])
proof_file = log_dir / f"FIX_v1_7_62_readonly_external_plugins_patch_{time.strftime('%Y%m%d_%H%M%S')}.txt"

fix_marker = "FIX_v1_7_62_INCLUDE_EXTERNAL_CHANNEL_PLUGINS"
secret_patterns = [
    re.compile(r"DISCORD_BOT_TOKEN="),
    re.compile(r"Bot\s+[A-Za-z0-9._-]{20,}"),
    re.compile(r"[A-Za-z0-9_-]{24}\.[A-Za-z0-9_-]{6}\.[A-Za-z0-9_-]{20,}"),
]

helper = r'''
async function __openclawFixV172IncludeExternalChannelPlugins(plugins) {
  /* FIX_v1_7_62_INCLUDE_EXTERNAL_CHANNEL_PLUGINS */
  if (!Array.isArray(plugins)) return plugins;
  if (plugins.some((plugin) => plugin && plugin.id === "discord")) return plugins;
  try {
    const fs = await import("node:fs");
    const os = await import("node:os");
    const path = await import("node:path");
    const url = await import("node:url");
    const projectsDir = path.join(os.homedir(), ".openclaw", "npm", "projects");
    if (!fs.existsSync(projectsDir)) return plugins;
    const projectNames = fs.readdirSync(projectsDir).filter((name) => name.startsWith("openclaw-discord-")).sort();
    for (let index = projectNames.length - 1; index >= 0; index -= 1) {
      const entryPath = path.join(projectsDir, projectNames[index], "node_modules", "@openclaw", "discord", "dist", "index.js");
      if (!fs.existsSync(entryPath)) continue;
      const entryModule = await import(url.pathToFileURL(entryPath).href);
      const entry = entryModule.default ?? entryModule;
      if (!entry || entry.id !== "discord" || typeof entry.loadChannelPlugin !== "function") continue;
      const loadedModule = await entry.loadChannelPlugin();
      const loadedPlugin = loadedModule && (loadedModule.default ?? loadedModule);
      if (loadedPlugin && loadedPlugin.id === "discord" && loadedPlugin.config && typeof loadedPlugin.config.listAccountIds === "function") {
        return [...plugins, loadedPlugin];
      }
    }
  } catch {
    return plugins;
  }
  return plugins;
}
'''

def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def token_scan(lines):
    text = "\n".join(lines)
    return not any(pattern.search(text) for pattern in secret_patterns)

def find_list_chunk():
    dist = openclaw_root / "dist"
    exact = dist / "list-CLFmilsU.js"
    candidates = [exact] if exact.exists() else []
    candidates.extend(path for path in sorted(dist.glob("list-*.js")) if path not in candidates)
    for path in candidates:
        text = path.read_text(encoding="utf-8", errors="replace")
        if "channelsListCommand" in text and "listReadOnlyChannelPluginsForConfig" in text and "catalogOnlyLines" in text:
            return path
    return None

def parse_public_discord(doc):
    if not isinstance(doc, dict):
        return {}, "UNKNOWN", "UNKNOWN"
    discord = doc.get("discord")
    if discord is None and isinstance(doc.get("chat"), dict):
        discord = doc["chat"].get("discord")
    if discord is None and isinstance(doc.get("channels"), dict):
        discord = doc["channels"].get("discord")
    if not isinstance(discord, dict):
        return {}, "UNKNOWN", "UNKNOWN"
    accounts = discord.get("accounts")
    if isinstance(accounts, list):
        count = str(len(accounts))
    elif isinstance(accounts, dict):
        count = str(len(accounts))
    else:
        count = "UNKNOWN"
    return discord, count, str(discord.get("origin", "UNKNOWN"))

def run_channels_json():
    proc = subprocess.run(
        ["openclaw", "channels", "list", "--all", "--json"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=45,
        env=os.environ.copy(),
    )
    start = proc.stdout.find("{")
    end = proc.stdout.rfind("}")
    doc = None
    if start >= 0 and end >= start:
        try:
            doc = json.loads(proc.stdout[start:end + 1])
        except Exception:
            doc = None
    _, count, origin = parse_public_discord(doc)
    return proc.returncode, count, origin

lines = []
result = "failed"
target = find_list_chunk()

try:
    if not openclaw_root.exists():
        raise RuntimeError("openclaw-root-missing")
    if target is None:
        raise RuntimeError("list-chunk-not-found")

    pre_hash = sha256_file(target)
    text = target.read_text(encoding="utf-8", errors="replace")

    if fix_marker in text:
        result = "already-present"
        backup = "not-created"
    else:
        if "async function channelsListCommand" not in text:
            result = "shape-mismatch"
            raise RuntimeError("channelsListCommand-not-async")

        needle = "const plugins = listReadOnlyChannelPluginsForConfig(cfg, { includeSetupFallbackPlugins: true });"
        replacement = (
            "let plugins = listReadOnlyChannelPluginsForConfig(cfg, { includeSetupFallbackPlugins: true });\n"
            "    plugins = await __openclawFixV172IncludeExternalChannelPlugins(plugins);"
        )
        if needle not in text:
            result = "shape-mismatch"
            raise RuntimeError("plugin-list-expression-not-found")

        insert_at = text.find("async function channelsListCommand")
        if insert_at < 0:
            result = "shape-mismatch"
            raise RuntimeError("channelsListCommand-insertion-point-not-found")

        backup_path = target.with_name(f"{target.name}.before-FIX_v1_7_62.{pre_hash[:16]}.bak")
        if not backup_path.exists():
            shutil.copy2(target, backup_path)
        backup = str(backup_path)

        patched = text[:insert_at] + helper + "\n" + text[insert_at:]
        patched = patched.replace(needle, replacement, 1)
        target.write_text(patched, encoding="utf-8")

        check = subprocess.run(["node", "--check", str(target)], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
        if check.returncode != 0:
            shutil.copy2(backup_path, target)
            result = "failed"
            raise RuntimeError("node-check-failed-restored-backup")
        result = "applied"

    post_hash = sha256_file(target)
    node_check = subprocess.run(["node", "--check", str(target)], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20)
    node_check_result = "PASS" if node_check.returncode == 0 else "FAIL"

    try:
        command_rc, account_count, public_origin = run_channels_json()
    except Exception:
        command_rc, account_count, public_origin = "UNKNOWN", "UNKNOWN", "UNKNOWN"

    lines.extend([
        f"PATCH_RESULT={result}",
        f"OPENCLAW_READONLY_PATCH_TARGET={target}",
        f"OPENCLAW_READONLY_PATCH_BACKUP={backup}",
        f"PATCH_TARGET_PRE_HASH={pre_hash}",
        f"PATCH_TARGET_POST_HASH={post_hash}",
        f"NODE_CHECK={node_check_result}",
        f"OPENCLAW_COMMAND_RETURN_CODE={command_rc}",
        f"PUBLIC_JSON_ACCOUNTS_COUNT_AFTER_PATCH={account_count}",
        f"PUBLIC_JSON_ORIGIN_AFTER_PATCH={public_origin}",
        "CONFIG_MUTATED=NO",
        "DISCORD_VERIFIER_RUN=NO",
        "DISCORD_ACTIVATION_CLAIMED=NO",
    ])
except Exception as exc:
    if target and target.exists():
        post_hash = sha256_file(target)
    else:
        post_hash = "UNKNOWN"
    lines.extend([
        f"PATCH_RESULT={result}",
        f"OPENCLAW_READONLY_PATCH_TARGET={target if target else 'UNKNOWN'}",
        "OPENCLAW_READONLY_PATCH_BACKUP=UNKNOWN",
        f"PATCH_TARGET_PRE_HASH={'UNKNOWN' if target is None else pre_hash if 'pre_hash' in locals() else 'UNKNOWN'}",
        f"PATCH_TARGET_POST_HASH={post_hash}",
        "NODE_CHECK=UNKNOWN",
        "PUBLIC_JSON_ACCOUNTS_COUNT_AFTER_PATCH=UNKNOWN",
        "PUBLIC_JSON_ORIGIN_AFTER_PATCH=UNKNOWN",
        "CONFIG_MUTATED=NO",
        "DISCORD_VERIFIER_RUN=NO",
        "DISCORD_ACTIVATION_CLAIMED=NO",
        f"ERROR_CLASS={exc.__class__.__name__}",
        f"ERROR_REASON={exc}",
    ])

if not token_scan(lines):
    print("TOKEN_LITERAL_SCAN=FAIL")
    print("DO_NOT_PASTE_OUTPUT=YES")
    sys.exit(1)

lines.append("TOKEN_LITERAL_SCAN=PASS")
ok = any(line in ("PATCH_RESULT=applied", "PATCH_RESULT=already-present") for line in lines)
ok = ok and any(line == "NODE_CHECK=PASS" for line in lines)
lines.append(f"FIX_v1_7_62_LIVE_PATCH_PROOF={'PASS' if ok else 'FAIL'}")
lines.append(f"PROOF_FILE={proof_file}")

proof_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
print("\n".join(lines))
PY
