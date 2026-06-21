#!/usr/bin/env bash
# redo_wsl_orchestrator_known_good.sh
#
# REDO WSL ORCHESTRATOR — known-good bootstrap.
#
# Target:
#   Fresh Ubuntu on WSL -> zsh/P10k -> system Node 24 -> Ollama GPU runtime ->
#   core Qwen model pack -> OpenClaw installed after Ollama -> default model set ->
#   gateway installed/running with local mode -> optional Discord token/owner config ->
#   optional Orchestrator repo restore.
#
# Design rule:
#   This script logs its own run as the build record. It does not rely on a later
#   fragile console-history capture step.

set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG_ROOT="${HOME}/orchestrator_bootstrap_logs"
LOG_DIR="${LOG_ROOT}/${STAMP}"
LOG_FILE="${LOG_DIR}/bootstrap.log"
SUMMARY_FILE="${LOG_DIR}/SUMMARY.md"
RED_DIR="${LOG_DIR}/redacted"
mkdir -p "$LOG_DIR" "$RED_DIR"

# Log everything from this point forward.
exec > >(tee -a "$LOG_FILE") 2>&1

YES=0
WITH_DISCORD=0
SKIP_MODELS=0
SKIP_OLLAMA=0
SKIP_OPENCLAW=0
ARCHIVE_PATH=""
MODEL_PACK="core"
OPENCLAW_PRIMARY="ollama/qwen3.6:35b"
OPENCLAW_FALLBACKS='["ollama/qwen3-coder:30b","ollama/qwen3:32b","ollama/qwen2.5-coder:32b","ollama/qwen3.5:9b","ollama/qwen3.5:4b","ollama/qwen3.5:2b","ollama/qwen3:0.6b"]'
DISCORD_OWNER_ID="${DISCORD_OWNER_ID:-}"
DISCORD_TOKEN_ENV="${DISCORD_TOKEN_ENV:-DISCORD_BOT_TOKEN}"
CODE_DIR="${HOME}/codex"
PROJECT_DIR="${CODE_DIR}/projects"

log() {
  printf '\n[%s] %s\n' "$SCRIPT_NAME" "$*"
}

die() {
  printf '\n[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2
  exit 1
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

usage() {
  cat <<'EOF'
Usage:
  bash redo_wsl_orchestrator_known_good.sh [options]

Options:
  --yes                         Assume yes for model pulls and non-secret prompts.
  --archive PATH                Restore Orchestrator repo from tar.gz archive.
  --model-pack core|minimal     Model pack to pull. Default: core.
  --skip-models                 Do not pull Ollama models.
  --skip-ollama                 Do not install/configure Ollama.
  --skip-openclaw               Do not install/configure OpenClaw.
  --with-discord                Configure Discord token env-ref and optional owner.
  --discord-owner-id ID         Set commands.ownerAllowFrom to ["discord:ID"].
  --discord-token-env NAME      Env var name for Discord token. Default: DISCORD_BOT_TOKEN.
  --primary MODEL               OpenClaw primary model. Default: ollama/qwen3.6:35b.
  --help                        Show this help.

Examples:
  bash redo_wsl_orchestrator_known_good.sh --yes

  bash redo_wsl_orchestrator_known_good.sh \
    --yes \
    --archive /mnt/c/Users/accou/Downloads/projects.tar.gz

  bash redo_wsl_orchestrator_known_good.sh \
    --yes \
    --with-discord \
    --discord-owner-id 150398348518490112
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --yes)
      YES=1
      shift
      ;;
    --archive)
      ARCHIVE_PATH="${2:-}"
      [[ -n "$ARCHIVE_PATH" ]] || die "--archive requires a path"
      shift 2
      ;;
    --model-pack)
      MODEL_PACK="${2:-}"
      [[ "$MODEL_PACK" == "core" || "$MODEL_PACK" == "minimal" ]] || die "--model-pack must be core or minimal"
      shift 2
      ;;
    --skip-models)
      SKIP_MODELS=1
      shift
      ;;
    --skip-ollama)
      SKIP_OLLAMA=1
      shift
      ;;
    --skip-openclaw)
      SKIP_OPENCLAW=1
      shift
      ;;
    --with-discord)
      WITH_DISCORD=1
      shift
      ;;
    --discord-owner-id)
      DISCORD_OWNER_ID="${2:-}"
      [[ -n "$DISCORD_OWNER_ID" ]] || die "--discord-owner-id requires a value"
      shift 2
      ;;
    --discord-token-env)
      DISCORD_TOKEN_ENV="${2:-}"
      [[ -n "$DISCORD_TOKEN_ENV" ]] || die "--discord-token-env requires a value"
      shift 2
      ;;
    --primary)
      OPENCLAW_PRIMARY="${2:-}"
      [[ -n "$OPENCLAW_PRIMARY" ]] || die "--primary requires a model"
      shift 2
      ;;
    --help|-h)
      usage
      exit 0
      ;;
    *)
      die "Unknown option: $1"
      ;;
  esac
done

on_error() {
  local rc=$?
  log "FAILED with exit code $rc"
  log "Log preserved at: $LOG_FILE"
  exit "$rc"
}
trap on_error ERR

log "Starting known-good bootstrap"
log "Log file: $LOG_FILE"

# Keep Windows npm shims from winning inside WSL.
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:${HOME}/bin:${HOME}/.local/bin"

if ! grep -qi microsoft /proc/version 2>/dev/null; then
  log "This does not look like WSL. Continuing anyway."
fi

if [[ "$(id -u)" == "0" ]]; then
  die "Run as your normal Linux user, not root."
fi

if command -v systemctl >/dev/null 2>&1 && systemctl is-system-running >/dev/null 2>&1; then
  log "systemd is active."
else
  log "systemd does not appear active. Enabling it in /etc/wsl.conf."
  sudo tee /etc/wsl.conf >/dev/null <<'EOF'
[boot]
systemd=true
EOF
  cat <<EOF

systemd has been enabled for future WSL launches.

From PowerShell, run:
  wsl --shutdown

Then reopen Ubuntu and rerun:
  bash ${HOME}/${SCRIPT_NAME} --yes

EOF
  exit 20
fi

log "Installing base Ubuntu packages"
sudo apt-get update || true
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
  ca-certificates curl wget git git-lfs gnupg software-properties-common \
  build-essential make cmake ninja-build pkg-config \
  python3 python3-dev python3-venv python3-pip pipx \
  jq ripgrep fd-find bat tree htop btop unzip zip tar xz-utils zstd rsync \
  nano vim tmux zsh fonts-font-awesome pciutils openssl lsb-release

log "Installing zsh, Oh My Zsh, Powerlevel10k, and zsh plugins"
if [[ ! -d "$HOME/.oh-my-zsh" ]]; then
  RUNZSH=no CHSH=no KEEP_ZSHRC=yes sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
fi

ZSH_CUSTOM="${ZSH_CUSTOM:-$HOME/.oh-my-zsh/custom}"
mkdir -p "$ZSH_CUSTOM/themes" "$ZSH_CUSTOM/plugins"

if [[ ! -d "$ZSH_CUSTOM/themes/powerlevel10k" ]]; then
  git clone --depth=1 https://github.com/romkatv/powerlevel10k.git "$ZSH_CUSTOM/themes/powerlevel10k"
fi
if [[ ! -d "$ZSH_CUSTOM/plugins/zsh-autosuggestions" ]]; then
  git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions "$ZSH_CUSTOM/plugins/zsh-autosuggestions"
fi
if [[ ! -d "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting" ]]; then
  git clone --depth=1 https://github.com/zsh-users/zsh-syntax-highlighting "$ZSH_CUSTOM/plugins/zsh-syntax-highlighting"
fi

touch "$HOME/.zshrc"
if ! grep -q 'ZSH_THEME="powerlevel10k/powerlevel10k"' "$HOME/.zshrc"; then
  if grep -q '^ZSH_THEME=' "$HOME/.zshrc"; then
    sed -i 's|^ZSH_THEME=.*|ZSH_THEME="powerlevel10k/powerlevel10k"|' "$HOME/.zshrc"
  else
    echo 'ZSH_THEME="powerlevel10k/powerlevel10k"' >> "$HOME/.zshrc"
  fi
fi

if grep -q '^plugins=' "$HOME/.zshrc"; then
  sed -i 's|^plugins=.*|plugins=(git zsh-autosuggestions zsh-syntax-highlighting)|' "$HOME/.zshrc"
else
  echo 'plugins=(git zsh-autosuggestions zsh-syntax-highlighting)' >> "$HOME/.zshrc"
fi

if ! grep -q 'REDO_WSL_ORCHESTRATOR_PATH_GUARD' "$HOME/.zshrc"; then
  cat >> "$HOME/.zshrc" <<'EOF'

# REDO_WSL_ORCHESTRATOR_PATH_GUARD
# Prefer native Linux tooling over inherited Windows npm shims.
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:$HOME/bin:$HOME/.local/bin:$PATH"
EOF
fi

ZSH_BIN="$(command -v zsh)"
if [[ "$SHELL" != "$ZSH_BIN" ]]; then
  log "Setting zsh as default shell for $USER"
  chsh -s "$ZSH_BIN" "$USER" || true
fi

log "Installing system Node.js 24"
if ! command -v node >/dev/null 2>&1 || ! node --version | grep -q '^v24\.'; then
  curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y nodejs
fi
hash -r
node --version
npm --version
which -a node npm || true

if [[ "$SKIP_OLLAMA" != "1" ]]; then
  log "Checking NVIDIA GPU visibility inside WSL"
  if ! command -v nvidia-smi >/dev/null 2>&1; then
    die "nvidia-smi not found inside WSL. Fix Windows NVIDIA/WSL GPU visibility before continuing."
  fi
  nvidia-smi || die "nvidia-smi failed"

  GPU_ID="$(nvidia-smi -L | sed -n 's/.*UUID: \(GPU-[^)]*\)).*/\1/p' | head -1 || true)"
  if [[ -z "$GPU_ID" ]]; then
    log "Could not parse GPU UUID. Falling back to CUDA_VISIBLE_DEVICES=0."
    GPU_ID="0"
  fi
  log "Selected CUDA_VISIBLE_DEVICES for Ollama: $GPU_ID"

  log "Installing Ollama"
  if ! command -v ollama >/dev/null 2>&1; then
    curl -fsSL https://ollama.com/install.sh | sh
  else
    log "Ollama already installed: $(ollama --version || true)"
  fi

  log "Configuring Ollama systemd service for WSL NVIDIA GPU"
  sudo mkdir -p /etc/systemd/system/ollama.service.d
  sudo tee /etc/systemd/system/ollama.service.d/override.conf >/dev/null <<EOF
[Service]
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
  for i in {1..60}; do
    if curl -fsS http://127.0.0.1:11434/api/version >/dev/null 2>&1; then
      break
    fi
    sleep 1
  done
  ollama --version
  curl -fsS http://127.0.0.1:11434/api/version || true

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
    log "WARNING: ollama ps did not show GPU usage. Check journalctl -u ollama and NVIDIA/WSL runtime."
  fi
fi

if [[ "$SKIP_OPENCLAW" != "1" ]]; then
  log "Installing OpenClaw after Ollama/model setup"
  sudo npm install -g openclaw@latest
  hash -r

  if ! command -v openclaw >/dev/null 2>&1; then
    die "openclaw command not found after npm install"
  fi
  if which openclaw | grep -q '^/mnt/c/'; then
    die "openclaw resolves to Windows npm shim. PATH is wrong: $(which openclaw)"
  fi
  openclaw --version

  log "Configuring OpenClaw model object"
  MODEL_JSON="{\"primary\":\"${OPENCLAW_PRIMARY}\",\"fallbacks\":${OPENCLAW_FALLBACKS}}"
  openclaw config set agents.defaults.model "$MODEL_JSON" --strict-json
  openclaw config get agents.defaults.model --json | tee "$LOG_DIR/openclaw_model_config.json"

  log "Configuring OpenClaw gateway local mode"
  openclaw config set gateway.mode local
  openclaw config set gateway.bind 127.0.0.1 || true

  log "Configuring OpenClaw gateway token"
  GATEWAY_TOKEN="${OPENCLAW_GATEWAY_TOKEN:-sk-OPENCLAW-$(openssl rand -hex 32)}"
  openclaw config set gateway.auth.mode token || true
  openclaw config set gateway.auth.token "$GATEWAY_TOKEN" || true

  log "Creating OpenClaw session store"
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

    mkdir -p "$HOME/.openclaw"
    umask 077
    printf '%s=%s\n' "$DISCORD_TOKEN_ENV" "${!DISCORD_TOKEN_ENV}" > "$HOME/.openclaw/.env"

    mkdir -p "$HOME/.config/environment.d"
    printf '%s=%s\n' "$DISCORD_TOKEN_ENV" "${!DISCORD_TOKEN_ENV}" > "$HOME/.config/environment.d/openclaw-discord.conf"
    chmod 600 "$HOME/.config/environment.d/openclaw-discord.conf" "$HOME/.openclaw/.env"

    openclaw config set channels.discord.token \
      --ref-provider default \
      --ref-source env \
      --ref-id "$DISCORD_TOKEN_ENV"

    openclaw config set channels.discord.enabled true --strict-json
    openclaw config set channels.discord.groupPolicy allowlist || true
    systemctl --user import-environment "$DISCORD_TOKEN_ENV" || true
  fi

  log "Installing/enabling OpenClaw gateway service"
  openclaw gateway install --force || openclaw gateway install || true
  loginctl enable-linger "$USER" || true
  systemctl --user daemon-reload
  systemctl --user enable openclaw-gateway.service || true
  systemctl --user restart openclaw-gateway.service

  sleep 3
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

log "Writing redacted config snapshots"
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
  echo "# REDO WSL ORCHESTRATOR known-good bootstrap summary"
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
  echo "## Key checks"
  echo "- Ollama ps after smoke: $LOG_DIR/ollama_ps_after_smoke.txt"
  echo "- OpenClaw gateway status: $LOG_DIR/openclaw_gateway_status.txt"
  echo "- OpenClaw gateway journal: $LOG_DIR/openclaw_gateway_journal_last120.txt"
  echo "- Redacted OpenClaw config: $RED_DIR/openclaw.redacted.json"
  echo
  echo "## Known-good target"
  echo "- Ollama installed and GPU-visible."
  echo "- Core Qwen model pack available when model pulls were enabled."
  echo "- OpenClaw installed after Ollama."
  echo "- OpenClaw model configured as ${OPENCLAW_PRIMARY}."
  echo "- OpenClaw gateway configured local and active."
  echo
  echo "## Remaining manual items"
  echo "- Windows Terminal font: select MesloLGS NF / Nerd Font for Powerlevel10k symbols."
  echo "- Discord Developer Portal: Message Content Intent and Server Members Intent must be enabled for Discord channel use."
  echo "- Discord server role: grant Manage Channels only if you want OpenClaw to create/manage channels."
} > "$SUMMARY_FILE"

log "Creating local evidence archive"
EVIDENCE_TAR="$HOME/orchestrator_known_good_bootstrap_${STAMP}.tar.gz"
tar -czf "$EVIDENCE_TAR" -C "$LOG_ROOT" "$STAMP"

# Copy archive to first writable Windows Downloads folder if available.
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

log "Completed known-good bootstrap"
cat "$SUMMARY_FILE"
