#!/usr/bin/env bash
# redo_wsl_orchestrator_one_shot_v3.sh
#
# REDO WSL ORCHESTRATOR — one-shot known-good bootstrap for fresh Ubuntu WSL.
#
# Intended first run:
#   bash redo_wsl_orchestrator_one_shot_v3.sh --yes
#
# Optional repo restore:
#   bash redo_wsl_orchestrator_one_shot_v3.sh --yes --archive /mnt/c/Users/accou/Downloads/projects.tar.gz
#
# Design:
#   - No reliance on old WSL state.
#   - System Node 24, not nvm, so OpenClaw's systemd gateway is stable.
#   - Handles WSL's NVIDIA shim path: /usr/lib/wsl/lib/nvidia-smi.
#   - Installs Ollama before OpenClaw.
#   - Pulls core local model pack before OpenClaw model config.
#   - Configures OpenClaw primary/fallback model schema correctly.
#   - Leaves a timestamped build log and evidence archive.

set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG_ROOT="${HOME}/orchestrator_bootstrap_logs"
LOG_DIR="${LOG_ROOT}/${STAMP}"
LOG_FILE="${LOG_DIR}/bootstrap.log"
SUMMARY_FILE="${LOG_DIR}/SUMMARY.md"
RED_DIR="${LOG_DIR}/redacted"

mkdir -p "$LOG_DIR" "$RED_DIR"
exec > >(tee -a "$LOG_FILE") 2>&1

YES=0
ARCHIVE_PATH=""
MODEL_PACK="core"
SKIP_MODELS=0
SKIP_OLLAMA=0
SKIP_OPENCLAW=0
WITH_DISCORD=0
DISCORD_OWNER_ID="${DISCORD_OWNER_ID:-}"
DISCORD_TOKEN_ENV="${DISCORD_TOKEN_ENV:-DISCORD_BOT_TOKEN}"
CODE_DIR="${HOME}/codex"
PROJECT_DIR="${CODE_DIR}/projects"

OPENCLAW_PRIMARY="ollama/qwen3.6:35b"
OPENCLAW_FALLBACKS='["ollama/qwen3-coder:30b","ollama/qwen3:32b","ollama/qwen2.5-coder:32b","ollama/qwen3.5:9b","ollama/qwen3.5:4b","ollama/qwen3.5:2b","ollama/qwen3:0.6b"]'

log() {
  printf '\n[%s] %s\n' "$SCRIPT_NAME" "$*"
}

die() {
  printf '\n[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2
  printf '[%s] Log preserved at: %s\n' "$SCRIPT_NAME" "$LOG_FILE" >&2
  exit 1
}

usage() {
  cat <<'EOF'
Usage:
  bash redo_wsl_orchestrator_one_shot_v3.sh [options]

Options:
  --yes                         Assume yes for non-secret prompts and model pulls.
  --archive PATH                Restore Orchestrator repo from a tar.gz archive.
  --model-pack core|minimal     Default: core.
  --skip-models                 Do not pull Ollama models.
  --skip-ollama                 Do not install/configure Ollama.
  --skip-openclaw               Do not install/configure OpenClaw.
  --with-discord                Configure Discord token env-ref and optional owner.
  --discord-owner-id ID         Set commands.ownerAllowFrom to ["discord:ID"].
  --discord-token-env NAME      Env var name for Discord token. Default: DISCORD_BOT_TOKEN.
  --primary MODEL               OpenClaw primary model. Default: ollama/qwen3.6:35b.
  --help                        Show this help.
EOF
}

ask_yes_no() {
  local prompt="$1"
  local default="${2:-n}"
  if [[ "$YES" == "1" ]]; then
    return 0
  fi
  local suffix="[y/N]"
  [[ "$default" == "y" ]] && suffix="[Y/n]"
  read -r -p "$prompt $suffix " ans || true
  ans="${ans:-$default}"
  [[ "$ans" =~ ^[Yy]$ ]]
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes) YES=1; shift ;;
    --archive) ARCHIVE_PATH="${2:-}"; [[ -n "$ARCHIVE_PATH" ]] || die "--archive requires path"; shift 2 ;;
    --model-pack) MODEL_PACK="${2:-}"; [[ "$MODEL_PACK" == "core" || "$MODEL_PACK" == "minimal" ]] || die "--model-pack must be core or minimal"; shift 2 ;;
    --skip-models) SKIP_MODELS=1; shift ;;
    --skip-ollama) SKIP_OLLAMA=1; shift ;;
    --skip-openclaw) SKIP_OPENCLAW=1; shift ;;
    --with-discord) WITH_DISCORD=1; shift ;;
    --discord-owner-id) DISCORD_OWNER_ID="${2:-}"; [[ -n "$DISCORD_OWNER_ID" ]] || die "--discord-owner-id requires value"; shift 2 ;;
    --discord-token-env) DISCORD_TOKEN_ENV="${2:-}"; [[ -n "$DISCORD_TOKEN_ENV" ]] || die "--discord-token-env requires value"; shift 2 ;;
    --primary) OPENCLAW_PRIMARY="${2:-}"; [[ -n "$OPENCLAW_PRIMARY" ]] || die "--primary requires model"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) die "Unknown option: $1" ;;
  esac
done

on_error() {
  local rc=$?
  log "FAILED with exit code $rc"
  log "Log preserved at: $LOG_FILE"
  exit "$rc"
}
trap on_error ERR

log "Starting one-shot bootstrap"
log "Log file: $LOG_FILE"

# WSL GPU utilities live here. Add this immediately before any checks.
if [[ -d /usr/lib/wsl/lib ]]; then
  export PATH="/usr/lib/wsl/lib:$PATH"
fi

# Prefer Linux tooling over inherited Windows PATH shims.
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/wsl/lib:${HOME}/bin:${HOME}/.local/bin:$PATH"

if [[ "$(id -u)" == "0" ]]; then
  die "Run as normal Linux user, not root."
fi

if ! grep -qi microsoft /proc/version 2>/dev/null; then
  log "This does not look like WSL. Continuing anyway."
fi

log "Checking systemd"
if command -v systemctl >/dev/null 2>&1 && systemctl is-system-running >/dev/null 2>&1; then
  log "systemd is active."
else
  log "systemd is not active. Enabling it in /etc/wsl.conf."
  sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true
EOF
  cat <<EOF

systemd was enabled for future WSL launches.

From POWERSHELL, not inside WSL, run:
  wsl --shutdown

Then reopen Ubuntu and rerun:
  bash ${HOME}/${SCRIPT_NAME} --yes

EOF
  exit 20
fi

log "Installing base Ubuntu packages"
sudo apt-get -o Acquire::Retries=5 update
sudo DEBIAN_FRONTEND=noninteractive apt-get -o Acquire::Retries=5 install -y \
  ca-certificates curl wget git git-lfs gnupg software-properties-common \
  build-essential make cmake ninja-build pkg-config \
  python3 python3-dev python3-venv python3-pip pipx \
  jq ripgrep fd-find bat tree htop btop unzip zip tar xz-utils zstd rsync \
  nano vim tmux zsh fonts-font-awesome pciutils openssl lsb-release

log "Persisting WSL GPU shim path for future shells"
if ! grep -q 'REDO_WSL_ORCHESTRATOR_WSL_GPU_PATH' "$HOME/.profile" 2>/dev/null; then
  cat >> "$HOME/.profile" <<'EOF'

# REDO_WSL_ORCHESTRATOR_WSL_GPU_PATH
if [ -d /usr/lib/wsl/lib ]; then
  export PATH="/usr/lib/wsl/lib:$PATH"
fi
EOF
fi

log "Installing zsh, Oh My Zsh, Powerlevel10k, and plugins"
if [[ ! -d "$HOME/.oh-my-zsh" ]]; then
  RUNZSH=no CHSH=no KEEP_ZSHRC=yes sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
fi

ZSH_CUSTOM="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"
mkdir -p "$ZSH_CUSTOM/themes" "$ZSH_CUSTOM/plugins"

[[ -d "$ZSH_CUSTOM/themes/powerlevel10k" ]] || git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "$ZSH_CUSTOM/themes/powerlevel10k"
[[ -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]] || git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions "$ZSH_CUSTOM/plugins/zsh-autosuggestions"
[[ -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]] || git clone --depth=1 https://github.com/zsh-users/zsh-syntax-highlighting "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting"

touch "$HOME/.zshrc"
if grep -q '^ZSH_THEME=' "$HOME/.zshrc"; then
  sed -i 's|^ZSH_THEME=.*|ZSH_THEME="powerlevel10k/powerlevel10k"|' "$HOME/.zshrc"
else
  echo 'ZSH_THEME="powerlevel10k/powerlevel10k"' >> "$HOME/.zshrc"
fi

if grep -q '^plugins=' "$HOME/.zshrc"; then
  sed -i 's|^plugins=.*|plugins=(git zsh-autosuggestions zsh-syntax-highlighting)|' "$HOME/.zshrc"
else
  echo 'plugins=(git zsh-autosuggestions zsh-syntax-highlighting)' >> "$HOME/.zshrc"
fi

if ! grep -q 'REDO_WSL_ORCHESTRATOR_PATH_GUARD' "$HOME/.zshrc"; then
  cat >> "$HOME/.zshrc" <<'EOF'

# REDO_WSL_ORCHESTRATOR_PATH_GUARD
if [ -d /usr/lib/wsl/lib ]; then
  export PATH="/usr/lib/wsl/lib:$PATH"
fi
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$HOME/bin:$HOME/.local/bin:$PATH"
EOF
fi

ZSH_BIN="$(command -v zsh)"
if [[ "$SHELL" != "$ZSH_BIN" ]]; then
  log "Setting zsh as default shell for $USER"
  sudo chsh -s "$ZSH_BIN" "$USER" || log "WARNING: chsh failed. zsh is installed; run: sudo chsh -s $ZSH_BIN $USER"
fi

log "Installing system Node.js 24"
if ! command -v node >/dev/null 2>&1 || ! node --version | grep -q '^v24\.'; then
  curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
  sudo DEBIAN_FRONTEND=noninteractive apt-get -o Acquire::Retries=5 install -y nodejs
fi
hash -r
node --version
npm --version
which -a node npm || true

if [[ "$SKIP_OLLAMA" != "1" ]]; then
  log "Checking NVIDIA GPU visibility inside WSL"
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    if [[ -x /usr/lib/wsl/lib/nvidia-smi ]]; then
      export PATH="/usr/lib/wsl/lib:$PATH"
    fi
  fi

  if ! command -v nvidia-smi >/dev/null 2>&1; then
    cat <<'EOF'

nvidia-smi is not visible inside WSL.

From POWERSHELL, not inside WSL, check:
  nvidia-smi
  wsl --status
  wsl --update
  wsl --shutdown

Then reopen Ubuntu and rerun this script.

Inside WSL, the expected NVIDIA shim is:
  /usr/lib/wsl/lib/nvidia-smi

Do not install a normal Linux NVIDIA display driver inside WSL.
EOF
    die "nvidia-smi not found inside WSL."
  fi

  nvidia-smi
  GPU_ID="$(nvidia-smi -L | sed -n 's/.*UUID: \(GPU-[^)]*\)).*/\1/p' | head -1 || true)"
  [[ -n "$GPU_ID" ]] || GPU_ID="0"
  log "Selected CUDA_VISIBLE_DEVICES for Ollama: $GPU_ID"

  log "Installing Ollama"
  if ! command -v ollama >/dev/null 2>&1; then
    curl -fsSL https://ollama.com/install.sh | sh
  else
    log "Ollama already installed: $(ollama --version || true)"
  fi

  log "Configuring Ollama systemd service for NVIDIA/WSL"
  sudo mkdir -p /etc/systemd/system/ollama.service.d
  sudo tee /etc/systemd/system/ollama.service.d/override.conf >/dev/null <<EOF
[Service]
Environment="PATH=/usr/lib/wsl/lib:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"
Environment="CUDA_VISIBLE_DEVICES=${GPU_ID}"
Environment="OLLAMA_HOST=127.0.0.1:11434"
Environment="OLLAMA_KEEP_ALIVE=30m"
Environment="OLLAMA_NUM_PARALLEL=1"
Environment="OLLAMA_MAX_LOADED_MODELS=1"
EOF

  sudo systemctl daemon-reload
  sudo systemctl enable ollama
  sudo systemctl restart ollama

  log "Waiting for Ollama API"
  for _ in {1..90}; do
    if curl -fsS http://127.0.0.1:11434/api/version >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
  curl -fsS http://127.0.0.1:11434/api/version || die "Ollama API did not become ready"
  ollama --version

  if [[ "$SKIP_MODELS" != "1" ]]; then
    if [[ "$MODEL_PACK" == "minimal" ]]; then
      MODELS=(qwen3:0.6b qwen3.5:4b qwen3-coder:30b)
    else
      MODELS=(qwen3:0.6b qwen3.6:35b qwen3:32b qwen3-coder:30b qwen2.5-coder:32b qwen3.5:9b qwen3.5:4b qwen3.5:2b)
    fi

    log "Models queued for pull: ${MODELS[*]}"
    if ask_yes_no "Pull these Ollama models now? This can download many tens of GB." "n"; then
      for model in "${MODELS[@]}"; do
        log "Pulling Ollama model: $model"
        ollama pull "$model"
      done
    else
      log "Skipping model pulls by user choice."
    fi
  fi

  log "Ollama model list"
  ollama list || true

  log "Running Ollama GPU smoke test with qwen3:0.6b"
  ollama pull qwen3:0.6b >/dev/null 2>&1 || true
  timeout 90s ollama run qwen3:0.6b "Reply with OK only." >/tmp/orchestrator_ollama_smoke.txt 2>&1 || true
  ollama ps | tee "$LOG_DIR/ollama_ps_after_smoke.txt" || true

  if ollama ps | grep -qi 'GPU'; then
    log "Ollama reports GPU usage."
  else
    log "WARNING: ollama ps did not show GPU usage. Check journalctl -u ollama."
  fi
fi

if [[ "$SKIP_OPENCLAW" != "1" ]]; then
  log "Installing OpenClaw after Ollama/model setup"
  sudo npm install -g openclaw@latest
  hash -r

  command -v openclaw >/dev/null 2>&1 || die "openclaw command not found after npm install"
  if which openclaw | grep -q '^/mnt/c/'; then
    die "openclaw resolves to Windows npm shim. PATH is wrong: $(which openclaw)"
  fi
  openclaw --version

  log "Configuring OpenClaw default model object"
  MODEL_JSON="{\"primary\":\"${OPENCLAW_PRIMARY}\",\"fallbacks\":${OPENCLAW_FALLBACKS}}"
  openclaw config set agents.defaults.model "$MODEL_JSON" --strict-json
  openclaw config get agents.defaults.model --json | tee "$LOG_DIR/openclaw_model_config.json"

  log "Configuring OpenClaw gateway local mode and token"
  openclaw config set gateway.mode local
  openclaw config set gateway.bind 127.0.0.1 || true

  GATEWAY_TOKEN="${OPENCLAW_GATEWAY_TOKEN:-sk-OPENCLAW-$(openssl rand -hex 32)}"
  openclaw config set gateway.auth.mode token || true
  openclaw config set gateway.auth.token "$GATEWAY_TOKEN" || true

  mkdir -p "$HOME/.openclaw/agents/main/sessions"

  if [[ -n "$DISCORD_OWNER_ID" ]]; then
    log "Configuring OpenClaw command owner for Discord ID: $DISCORD_OWNER_ID"
    openclaw config set commands.ownerAllowFrom "[\"discord:${DISCORD_OWNER_ID}\"]" --strict-json
  fi

  if [[ "$WITH_DISCORD" == "1" ]]; then
    log "Configuring Discord channel token env-ref"
    if [[ -z "${!DISCORD_TOKEN_ENV:-}" ]]; then
      read -rsp "Paste Discord bot token for ${DISCORD_TOKEN_ENV}: " TOKEN_INPUT
      echo
      export "${DISCORD_TOKEN_ENV}=${TOKEN_INPUT}"
    fi

    mkdir -p "$HOME/.openclaw" "$HOME/.config/environment.d"
    umask 077
    printf '%s=%s\n' "$DISCORD_TOKEN_ENV" "${!DISCORD_TOKEN_ENV}" > "$HOME/.openclaw/.env"
    printf '%s=%s\n' "$DISCORD_TOKEN_ENV" "${!DISCORD_TOKEN_ENV}" > "$HOME/.config/environment.d/openclaw-discord.conf"
    chmod 600 "$HOME/.openclaw/.env" "$HOME/.config/environment.d/openclaw-discord.conf"

    openclaw config set channels.discord.token \
      --ref-provider default \
      --ref-source env \
      --ref-id "$DISCORD_TOKEN_ENV"
    openclaw config set channels.discord.enabled true --strict-json
    openclaw config set channels.discord.groupPolicy allowlist || true
    systemctl --user import-environment "$DISCORD_TOKEN_ENV" || true
  fi

  log "Installing and starting OpenClaw gateway service"
  openclaw gateway install --force || openclaw gateway install || true
  sudo loginctl enable-linger "$USER" || true
  systemctl --user daemon-reload
  systemctl --user enable openclaw-gateway.service || true
  systemctl --user restart openclaw-gateway.service

  sleep 5
  systemctl --user status openclaw-gateway.service --no-pager | tee "$LOG_DIR/openclaw_gateway_status.txt" || true
  journalctl --user -u openclaw-gateway.service -n 120 --no-pager | tee "$LOG_DIR/openclaw_gateway_journal_last120.txt" || true

  if systemctl --user is-active --quiet openclaw-gateway.service; then
    log "OpenClaw gateway is active."
  else
    die "OpenClaw gateway did not become active."
  fi
fi

restore_archive() {
  local archive="$1"
  [[ -f "$archive" ]] || die "Archive not found: $archive"

  log "Restoring Orchestrator from archive: $archive"
  mkdir -p "$CODE_DIR"

  local prefix=""
  if tar -tf "$archive" | grep -q '^projects/'; then
    prefix="projects"
  elif tar -tf "$archive" | grep -q '^codex/projects/'; then
    prefix="codex/projects"
  elif tar -tf "$archive" | grep -q '^home/roger/codex/projects/'; then
    prefix="home/roger/codex/projects"
  else
    die "Could not find projects/, codex/projects/, or home/roger/codex/projects/ inside archive."
  fi

  local tmp
  tmp="$(mktemp -d)"
  tar -xzf "$archive" -C "$tmp" "$prefix"

  mkdir -p "$PROJECT_DIR"
  rsync -a --delete \
    --exclude='.venv' \
    --exclude='venv' \
    --exclude='node_modules' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='*:Zone.Identifier' \
    "$tmp/$prefix/" "$PROJECT_DIR/"

  rm -rf "$tmp"

  find "$PROJECT_DIR" -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
  find "$PROJECT_DIR" -name '*.pyc' -delete 2>/dev/null || true
  find "$PROJECT_DIR" -name '*:Zone.Identifier' -delete 2>/dev/null || true

  log "Orchestrator restored to: $PROJECT_DIR"

  if [[ -f "$PROJECT_DIR/main.py" ]]; then
    python3 -m venv "$PROJECT_DIR/.venv"
    # shellcheck disable=SC1091
    source "$PROJECT_DIR/.venv/bin/activate"
    (cd "$PROJECT_DIR" && python main.py --help >/dev/null 2>&1 || true)
    deactivate || true
  fi

  mkdir -p "$HOME/bin"
  cat > "$HOME/bin/orch" <<EOF
#!/usr/bin/env bash
cd "$PROJECT_DIR" || exit 1
if [ -f ".venv/bin/activate" ]; then
  source ".venv/bin/activate"
fi
exec python main.py "\$@"
EOF
  chmod +x "$HOME/bin/orch"
}

if [[ -n "$ARCHIVE_PATH" ]]; then
  restore_archive "$ARCHIVE_PATH"
else
  log "No --archive provided. Skipping Orchestrator restore."
fi

log "Writing redacted OpenClaw config snapshot"
if [[ -f "$HOME/.openclaw/openclaw.json" ]]; then
  python3 - <<'PY' > "$RED_DIR/openclaw.redacted.json" 2>/dev/null || true
import json, os
p=os.path.expanduser("~/.openclaw/openclaw.json")
data=json.load(open(p))
def redact(x):
    if isinstance(x, dict):
        out={}
        for k,v in x.items():
            if any(s in k.lower() for s in ["token","secret","password","key"]):
                out[k]="<REDACTED>"
            else:
                out[k]=redact(v)
        return out
    if isinstance(x, list):
        return [redact(v) for v in x]
    return x
print(json.dumps(redact(data), indent=2, sort_keys=True))
PY
fi

log "Writing summary"
{
  echo "# REDO WSL ORCHESTRATOR one-shot bootstrap summary"
  echo
  echo "Created: $(date -Iseconds)"
  echo "User: $USER"
  echo "Host: $(hostname)"
  echo "Log: $LOG_FILE"
  echo
  echo "## Versions"
  command -v node >/dev/null && echo "node: $(node --version)"
  command -v npm >/dev/null && echo "npm: $(npm --version)"
  command -v openclaw >/dev/null && echo "openclaw: $(openclaw --version)"
  command -v ollama >/dev/null && echo "ollama: $(ollama --version)"
  command -v zsh >/dev/null && echo "zsh: $(zsh --version)"
  echo
  echo "## Evidence"
  echo "- Ollama ps after smoke: $LOG_DIR/ollama_ps_after_smoke.txt"
  echo "- OpenClaw gateway status: $LOG_DIR/openclaw_gateway_status.txt"
  echo "- OpenClaw gateway journal: $LOG_DIR/openclaw_gateway_journal_last120.txt"
  echo "- Redacted OpenClaw config: $RED_DIR/openclaw.redacted.json"
  echo
  echo "## Manual items"
  echo "- Close/reopen WSL after completion so zsh becomes the login shell."
  echo "- Windows Terminal font: select MesloLGS NF / Nerd Font for Powerlevel10k."
  echo "- Discord Developer Portal intents are separate if --with-discord is used."
} > "$SUMMARY_FILE"

log "Creating evidence archive"
EVIDENCE_TAR="$HOME/orchestrator_one_shot_bootstrap_${STAMP}.tar.gz"
tar -czf "$EVIDENCE_TAR" -C "$LOG_ROOT" "$STAMP"

EXPORT_DIR=""
for d in /mnt/c/Users/*/Downloads; do
  if [[ -d "$d" && -w "$d" ]]; then
    EXPORT_DIR="$d"
    break
  fi
done

if [[ -n "$EXPORT_DIR" ]]; then
  cp "$EVIDENCE_TAR" "$EXPORT_DIR/" || true
  log "Evidence archive copied to: $EXPORT_DIR/$(basename "$EVIDENCE_TAR")"
fi

log "Completed one-shot bootstrap"
cat "$SUMMARY_FILE"
