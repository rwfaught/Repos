#!/usr/bin/env bash
# REDO WSL ORCHESTRATOR fresh Ubuntu bootstrap — GPU/model-first edition
# Target: fresh Ubuntu on WSL2 -> systemd -> dev base -> zsh/p10k -> Node -> Ollama GPU validation -> model pack -> OpenClaw -> Orchestrator restore.
#
# Design rule: do not install/configure OpenClaw until Ollama is installed, GPU-visible, and the chosen local model stack is present.
# Safe default: does not restore your old home directory. If you pass a full /home/roger backup,
# it attempts to extract only the Orchestrator project subtree.

set -Eeuo pipefail
IFS=$'\n\t'

SCRIPT_NAME="$(basename "$0")"
CODEX_DIR="${CODEX_DIR:-$HOME/codex}"
ORCH_ARCHIVE="${ORCH_ARCHIVE:-}"
OPENCLAW_ONBOARD=0
INSTALL_OPENCLAW=1
INSTALL_OLLAMA=1
PULL_MODEL=""
RUN_TESTS=1
FORCE=0
YES=0
SKIP_GPU_VALIDATE=0
SKIP_MODEL_SMOKE_TEST=0
MODEL_PACK="${MODEL_PACK:-core}"
OPENCLAW_DEFAULT_MODEL="${OPENCLAW_DEFAULT_MODEL:-qwen3.6:35b}"
OPENCLAW_FALLBACK_MODEL="${OPENCLAW_FALLBACK_MODEL:-qwen3-coder:30b}"
OLLAMA_GPU_ID="${OLLAMA_GPU_ID:-auto}"
OLLAMA_FORCE_LLM_LIBRARY="${OLLAMA_FORCE_LLM_LIBRARY:-}"
OLLAMA_CONTEXT_LENGTH="${OLLAMA_CONTEXT_LENGTH:-32768}"
OLLAMA_KEEP_ALIVE="${OLLAMA_KEEP_ALIVE:-30m}"
OLLAMA_MAX_LOADED_MODELS="${OLLAMA_MAX_LOADED_MODELS:-1}"
OLLAMA_NUM_PARALLEL="${OLLAMA_NUM_PARALLEL:-1}"
OLLAMA_LOAD_TIMEOUT="${OLLAMA_LOAD_TIMEOUT:-30m}"
GPU_TEST_MODEL="${GPU_TEST_MODEL:-qwen3:0.6b}"
EXTRA_MODELS=()

log()  { printf '\n\033[1;32m[orchestrator-bootstrap]\033[0m %s\n' "$*"; }
warn() { printf '\n\033[1;33m[warn]\033[0m %s\n' "$*" >&2; }
die()  { printf '\n\033[1;31m[error]\033[0m %s\n' "$*" >&2; exit 1; }

usage() {
  cat <<'USAGE'
Usage:
  bash redo_wsl_orchestrator_fresh_gpu_models.sh [options]

Options:
  --archive PATH              Restore Orchestrator from a repo tarball OR from a full old-home tarball.
                              The script searches for projects/, codex/projects/, or home/roger/codex/projects.
  --onboard                   Run: openclaw onboard --install-daemon after installing OpenClaw.
  --no-openclaw               Skip OpenClaw install.
  --no-ollama                 Skip Ollama install and model pulls.
  --model-pack NAME           Model pack to pull before OpenClaw. Default: core.
                              Choices: none, minimal, core, full.
  --pull-model NAME           Pull one additional Ollama model. Can be repeated.
  --openclaw-model NAME       Default OpenClaw Ollama model. Default: qwen3.6:35b.
  --openclaw-fallback NAME    Fallback OpenClaw Ollama model. Default: qwen3-coder:30b.
  --ollama-gpu ID             CUDA_VISIBLE_DEVICES value for Ollama. Default: auto.
                              auto uses the first NVIDIA GPU UUID from nvidia-smi when available.
  --force-cuda-library NAME   Optional OLLAMA_LLM_LIBRARY override, e.g. cuda_v12, cuda_v13.
                              Leave unset unless autodetection fails.
  --context-length N          OLLAMA_CONTEXT_LENGTH. Default: 32768.
  --yes                       Do not ask before large model downloads.
  --skip-gpu-validate         Do not fail if nvidia-smi/GPU validation fails.
  --skip-model-smoke-test     Pull models but skip the runtime GPU smoke test.
  --no-tests                  Do not run Orchestrator unittest discovery after restore.
  --force                     Continue through more non-critical failures.
  -h, --help                  Show this help.

Model packs:
  minimal:
    qwen3:0.6b
    qwen3.6:35b
    qwen3-coder:30b
    qwen3.5:9b
    qwen3.5:2b

  core [default]:
    qwen3:0.6b
    qwen3.6:35b
    qwen3:32b
    qwen3-coder:30b
    qwen2.5-coder:32b
    qwen3.5:9b
    qwen3.5:4b
    qwen3.5:2b

  full:
    core plus qwen3.6:27b, qwen3:30b, qwen3:14b, qwen3:8b, qwen2.5-coder:14b, qwen2.5-coder:7b

Examples:
  bash redo_wsl_orchestrator_fresh_gpu_models.sh --model-pack core --onboard

  bash redo_wsl_orchestrator_fresh_gpu_models.sh \
    --archive /mnt/c/Users/Roger/Downloads/orchestrator_repo_backup.tar.gz \
    --model-pack core \
    --openclaw-model qwen3.6:35b \
    --onboard

Notes:
  - Run this inside the NEW Ubuntu WSL distro, not PowerShell.
  - If systemd is not active, the script writes /etc/wsl.conf and stops.
    Then run from PowerShell: wsl --shutdown
    Reopen the new Ubuntu distro and run this script again.
  - The script cannot make a too-large model fit entirely into VRAM. It configures Ollama for NVIDIA visibility,
    validates GPU discovery, and fails before OpenClaw if the smoke test is CPU-only.
USAGE
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --archive)
      [[ $# -ge 2 ]] || die "--archive requires a path"
      ORCH_ARCHIVE="$2"
      shift 2
      ;;
    --onboard)
      OPENCLAW_ONBOARD=1
      shift
      ;;
    --no-openclaw)
      INSTALL_OPENCLAW=0
      shift
      ;;
    --no-ollama)
      INSTALL_OLLAMA=0
      MODEL_PACK="none"
      shift
      ;;
    --model-pack)
      [[ $# -ge 2 ]] || die "--model-pack requires a name"
      MODEL_PACK="$2"
      shift 2
      ;;
    --pull-model)
      [[ $# -ge 2 ]] || die "--pull-model requires a model name"
      EXTRA_MODELS+=("$2")
      shift 2
      ;;
    --openclaw-model)
      [[ $# -ge 2 ]] || die "--openclaw-model requires a model name"
      OPENCLAW_DEFAULT_MODEL="$2"
      shift 2
      ;;
    --openclaw-fallback)
      [[ $# -ge 2 ]] || die "--openclaw-fallback requires a model name"
      OPENCLAW_FALLBACK_MODEL="$2"
      shift 2
      ;;
    --ollama-gpu)
      [[ $# -ge 2 ]] || die "--ollama-gpu requires a CUDA_VISIBLE_DEVICES value"
      OLLAMA_GPU_ID="$2"
      shift 2
      ;;
    --force-cuda-library)
      [[ $# -ge 2 ]] || die "--force-cuda-library requires a library name"
      OLLAMA_FORCE_LLM_LIBRARY="$2"
      shift 2
      ;;
    --context-length)
      [[ $# -ge 2 ]] || die "--context-length requires a number"
      OLLAMA_CONTEXT_LENGTH="$2"
      shift 2
      ;;
    --yes)
      YES=1
      shift
      ;;
    --skip-gpu-validate)
      SKIP_GPU_VALIDATE=1
      shift
      ;;
    --skip-model-smoke-test)
      SKIP_MODEL_SMOKE_TEST=1
      shift
      ;;
    --no-tests)
      RUN_TESTS=0
      shift
      ;;
    --force)
      FORCE=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      die "Unknown option: $1"
      ;;
  esac
done

run_or_warn() {
  if ! "$@"; then
    if [[ "$FORCE" == "1" ]]; then
      warn "Command failed but --force is set: $*"
      return 0
    fi
    return 1
  fi
}

need_cmd() {
  command -v "$1" >/dev/null 2>&1
}

ensure_not_root() {
  [[ "${EUID}" -ne 0 ]] || die "Do not run this script as root. Run it as your normal WSL user."
}

ensure_wsl() {
  if ! grep -qiE 'microsoft|wsl' /proc/version 2>/dev/null; then
    warn "This does not look like WSL from /proc/version. Continuing anyway."
  fi
}

ensure_systemd() {
  local init_name
  init_name="$(ps -p 1 -o comm= 2>/dev/null || true)"

  if [[ "$init_name" == "systemd" ]]; then
    log "systemd is active."
    return 0
  fi

  warn "systemd is not active. OpenClaw's managed gateway and Ollama's service configuration expect systemd in WSL."
  warn "Writing /etc/wsl.conf so systemd starts on next WSL launch."

  sudo cp /etc/wsl.conf "/etc/wsl.conf.bak.$(date +%Y%m%d_%H%M%S)" 2>/dev/null || true
  sudo tee /etc/wsl.conf >/dev/null <<EOWSL
[boot]
systemd=true

[user]
default=$USER
EOWSL

  cat <<EOFMSG

Systemd has been enabled for the NEXT WSL launch.

Now run this in POWERSHELL, not inside Linux:

  wsl --shutdown

Then reopen this new Ubuntu distro and rerun this script.

EOFMSG
  exit 20
}

apt_install_base() {
  log "Installing base Ubuntu packages."
  sudo apt-get update
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y \
    ca-certificates \
    curl \
    wget \
    git \
    git-lfs \
    build-essential \
    make \
    gcc \
    g++ \
    pkg-config \
    cmake \
    ninja-build \
    unzip \
    zip \
    tar \
    zstd \
    xz-utils \
    rsync \
    jq \
    ripgrep \
    fd-find \
    bat \
    tree \
    htop \
    btop \
    tmux \
    zsh \
    nano \
    vim \
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    pipx \
    openssh-client \
    software-properties-common \
    gnupg \
    lsb-release \
    pciutils

  mkdir -p "$HOME/bin" "$HOME/.local/bin"

  # Debian/Ubuntu package names expose fd and bat with alternate binary names.
  if need_cmd fdfind && ! need_cmd fd; then
    ln -sf "$(command -v fdfind)" "$HOME/bin/fd"
  fi
  if need_cmd batcat && ! need_cmd bat; then
    ln -sf "$(command -v batcat)" "$HOME/bin/bat"
  fi

  python3 -m pipx ensurepath >/dev/null 2>&1 || true
}

install_ohmyzsh_p10k() {
  log "Installing zsh, Oh My Zsh, Powerlevel10k, and useful zsh plugins."

  if [[ ! -d "$HOME/.oh-my-zsh" ]]; then
    RUNZSH=no CHSH=no KEEP_ZSHRC=yes \
      sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
  fi

  mkdir -p "$HOME/.oh-my-zsh/custom/themes" "$HOME/.oh-my-zsh/custom/plugins"

  if [[ ! -d "$HOME/.oh-my-zsh/custom/themes/powerlevel10k" ]]; then
    git clone --depth=1 https://github.com/romkatv/powerlevel10k.git \
      "$HOME/.oh-my-zsh/custom/themes/powerlevel10k"
  fi

  if [[ ! -d "$HOME/.oh-my-zsh/custom/plugins/zsh-autosuggestions" ]]; then
    git clone --depth=1 https://github.com/zsh-users/zsh-autosuggestions \
      "$HOME/.oh-my-zsh/custom/plugins/zsh-autosuggestions"
  fi

  if [[ ! -d "$HOME/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting" ]]; then
    git clone --depth=1 https://github.com/zsh-users/zsh-syntax-highlighting.git \
      "$HOME/.oh-my-zsh/custom/plugins/zsh-syntax-highlighting"
  fi

  touch "$HOME/.zshrc"

  if grep -q '^ZSH_THEME=' "$HOME/.zshrc"; then
    sed -i 's#^ZSH_THEME=.*#ZSH_THEME="powerlevel10k/powerlevel10k"#' "$HOME/.zshrc"
  else
    printf '\nZSH_THEME="powerlevel10k/powerlevel10k"\n' >> "$HOME/.zshrc"
  fi

  if grep -q '^plugins=' "$HOME/.zshrc"; then
    sed -i 's#^plugins=.*#plugins=(git zsh-autosuggestions zsh-syntax-highlighting)#' "$HOME/.zshrc"
  else
    printf '\nplugins=(git zsh-autosuggestions zsh-syntax-highlighting)\n' >> "$HOME/.zshrc"
  fi

  local marker_start="# >>> orchestrator bootstrap >>>"
  local marker_end="# <<< orchestrator bootstrap <<<"
  awk -v start="$marker_start" -v end="$marker_end" '
    $0 == start {skip=1; next}
    $0 == end {skip=0; next}
    skip != 1 {print}
  ' "$HOME/.zshrc" > "$HOME/.zshrc.tmp"
  mv "$HOME/.zshrc.tmp" "$HOME/.zshrc"

  cat >> "$HOME/.zshrc" <<'EOZSH'

# >>> orchestrator bootstrap >>>
export PATH="$HOME/bin:$HOME/.local/bin:/usr/lib/wsl/lib:$PATH"
export EDITOR="${EDITOR:-nano}"

[[ -f ~/.p10k.zsh ]] && source ~/.p10k.zsh

alias ll='ls -alF'
alias la='ls -A'
alias l='ls -CF'
alias py='python3'
alias orch='cd ~/codex/projects && source .venv/bin/activate 2>/dev/null || true; python main.py'
alias om='ollama list'
alias ops='ollama ps'
alias ogpu='ollama-gpu-check'
# <<< orchestrator bootstrap <<<
EOZSH

  if [[ "${SHELL:-}" != "$(command -v zsh)" ]]; then
    log "Setting zsh as default shell for $USER."
    sudo chsh -s "$(command -v zsh)" "$USER" || warn "Could not change login shell automatically. You can run: chsh -s $(command -v zsh)"
  fi
}

install_node_nvm() {
  log "Installing nvm and Node.js 24."
  export NVM_DIR="$HOME/.nvm"

  if [[ ! -s "$NVM_DIR/nvm.sh" ]]; then
    mkdir -p "$NVM_DIR"
    curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
  fi

  # shellcheck disable=SC1091
  source "$NVM_DIR/nvm.sh"

  nvm install 24
  nvm alias default 24
  nvm use 24

  node --version
  npm --version

  if ! grep -q 'NVM_DIR' "$HOME/.zshrc"; then
    cat >> "$HOME/.zshrc" <<'EONVM'

export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"
[ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"
EONVM
  fi
}

find_nvidia_smi() {
  if need_cmd nvidia-smi; then
    command -v nvidia-smi
    return 0
  fi
  if [[ -x /usr/lib/wsl/lib/nvidia-smi ]]; then
    printf '%s\n' /usr/lib/wsl/lib/nvidia-smi
    return 0
  fi
  return 1
}

detect_cuda_visible_devices() {
  if [[ "$OLLAMA_GPU_ID" != "auto" ]]; then
    printf '%s\n' "$OLLAMA_GPU_ID"
    return 0
  fi

  local smi uuid
  smi="$(find_nvidia_smi 2>/dev/null || true)"
  if [[ -n "$smi" ]]; then
    uuid="$($smi --query-gpu=uuid --format=csv,noheader 2>/dev/null | head -n 1 | tr -d '[:space:]' || true)"
    if [[ -n "$uuid" ]]; then
      printf '%s\n' "$uuid"
      return 0
    fi
  fi

  printf '0\n'
}

preflight_gpu() {
  [[ "$SKIP_GPU_VALIDATE" == "0" ]] || { log "Skipping GPU preflight by request."; return 0; }

  log "Checking NVIDIA GPU visibility inside WSL."
  local smi
  smi="$(find_nvidia_smi 2>/dev/null || true)"
  if [[ -z "$smi" ]]; then
    die "nvidia-smi is not visible inside WSL. Confirm Windows NVIDIA driver + WSL GPU bridge before pulling large models. Use --skip-gpu-validate only if you know GPU is working."
  fi

  "$smi" || die "nvidia-smi exists but failed. Fix GPU visibility before continuing."

  log "Selected CUDA_VISIBLE_DEVICES for Ollama: $(detect_cuda_visible_devices)"
}

install_ollama() {
  [[ "$INSTALL_OLLAMA" == "1" ]] || { log "Skipping Ollama install."; return 0; }

  log "Installing Ollama."
  if ! need_cmd ollama; then
    curl -fsSL https://ollama.com/install.sh | sh
  fi

  configure_ollama_service
  start_ollama_service
  wait_for_ollama

  ollama --version || true
}

configure_ollama_service() {
  [[ "$INSTALL_OLLAMA" == "1" ]] || return 0

  log "Configuring Ollama service for WSL NVIDIA GPU visibility."

  local cuda_devices
  cuda_devices="$(detect_cuda_visible_devices)"

  sudo mkdir -p /etc/systemd/system/ollama.service.d

  {
    printf '[Service]\n'
    printf 'Environment="PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin:/usr/lib/wsl/lib"\n'
    printf 'Environment="LD_LIBRARY_PATH=/usr/lib/wsl/lib"\n'
    printf 'Environment="CUDA_VISIBLE_DEVICES=%s"\n' "$cuda_devices"
    printf 'Environment="OLLAMA_HOST=127.0.0.1:11434"\n'
    printf 'Environment="OLLAMA_KEEP_ALIVE=%s"\n' "$OLLAMA_KEEP_ALIVE"
    printf 'Environment="OLLAMA_MAX_LOADED_MODELS=%s"\n' "$OLLAMA_MAX_LOADED_MODELS"
    printf 'Environment="OLLAMA_NUM_PARALLEL=%s"\n' "$OLLAMA_NUM_PARALLEL"
    printf 'Environment="OLLAMA_CONTEXT_LENGTH=%s"\n' "$OLLAMA_CONTEXT_LENGTH"
    printf 'Environment="OLLAMA_LOAD_TIMEOUT=%s"\n' "$OLLAMA_LOAD_TIMEOUT"
    printf 'Environment="OLLAMA_FLASH_ATTENTION=1"\n'
    if [[ -n "$OLLAMA_FORCE_LLM_LIBRARY" ]]; then
      printf 'Environment="OLLAMA_LLM_LIBRARY=%s"\n' "$OLLAMA_FORCE_LLM_LIBRARY"
    fi
  } | sudo tee /etc/systemd/system/ollama.service.d/orchestrator-gpu.conf >/dev/null

  sudo systemctl daemon-reload
}

start_ollama_service() {
  log "Starting Ollama service."
  sudo systemctl enable --now ollama >/dev/null 2>&1 || warn "Could not enable/start Ollama system service automatically."
  sudo systemctl restart ollama || warn "Could not restart Ollama service."
}

wait_for_ollama() {
  log "Waiting for Ollama API."
  local i
  for i in {1..60}; do
    if curl -fsS http://127.0.0.1:11434/api/tags >/dev/null 2>&1; then
      return 0
    fi
    sleep 1
  done
  die "Ollama API did not become ready at 127.0.0.1:11434. Check: journalctl -u ollama -n 120 --no-pager"
}

models_for_pack() {
  case "$MODEL_PACK" in
    none)
      return 0
      ;;
    minimal)
      cat <<'EOMODELS'
qwen3:0.6b
qwen3.6:35b
qwen3-coder:30b
qwen3.5:9b
qwen3.5:2b
EOMODELS
      ;;
    core)
      cat <<'EOMODELS'
qwen3:0.6b
qwen3.6:35b
qwen3:32b
qwen3-coder:30b
qwen2.5-coder:32b
qwen3.5:9b
qwen3.5:4b
qwen3.5:2b
EOMODELS
      ;;
    full)
      cat <<'EOMODELS'
qwen3:0.6b
qwen3.6:35b
qwen3.6:27b
qwen3:32b
qwen3:30b
qwen3-coder:30b
qwen2.5-coder:32b
qwen2.5-coder:14b
qwen2.5-coder:7b
qwen3:14b
qwen3:8b
qwen3.5:9b
qwen3.5:4b
qwen3.5:2b
EOMODELS
      ;;
    *)
      die "Unknown --model-pack: $MODEL_PACK. Use none, minimal, core, or full."
      ;;
  esac
}

collect_models() {
  local model seen_key
  declare -A seen=()

  while IFS= read -r model; do
    [[ -n "$model" ]] || continue
    seen_key="$model"
    if [[ -z "${seen[$seen_key]+x}" ]]; then
      printf '%s\n' "$model"
      seen[$seen_key]=1
    fi
  done < <(models_for_pack)

  for model in "${EXTRA_MODELS[@]}"; do
    [[ -n "$model" ]] || continue
    seen_key="$model"
    if [[ -z "${seen[$seen_key]+x}" ]]; then
      printf '%s\n' "$model"
      seen[$seen_key]=1
    fi
  done
}

confirm_model_downloads() {
  [[ "$INSTALL_OLLAMA" == "1" ]] || return 0
  [[ "$MODEL_PACK" != "none" || "${#EXTRA_MODELS[@]}" -gt 0 ]] || return 0

  mapfile -t models < <(collect_models)
  [[ "${#models[@]}" -gt 0 ]] || return 0

  cat <<EOFMSG

Model pack: $MODEL_PACK
OpenClaw default model:  $OPENCLAW_DEFAULT_MODEL
OpenClaw fallback model: $OPENCLAW_FALLBACK_MODEL

Models queued for pull before OpenClaw:
$(printf '  - %s\n' "${models[@]}")

This can download many tens of GB. The core pack is intentionally heavy because it makes this machine useful immediately for local Orchestrator work.
EOFMSG

  if [[ "$YES" == "1" ]]; then
    return 0
  fi

  local reply
  read -r -p "Continue pulling these models now? [y/N] " reply
  case "$reply" in
    y|Y|yes|YES) return 0 ;;
    *) die "Model pull cancelled. Re-run with --model-pack minimal/core/full or --yes." ;;
  esac
}

pull_ollama_models() {
  [[ "$INSTALL_OLLAMA" == "1" ]] || return 0
  [[ "$MODEL_PACK" != "none" || "${#EXTRA_MODELS[@]}" -gt 0 ]] || { log "No Ollama model pack selected."; return 0; }

  confirm_model_downloads

  local model
  while IFS= read -r model; do
    [[ -n "$model" ]] || continue
    log "Pulling Ollama model: $model"
    ollama pull "$model"
  done < <(collect_models)

  log "Ollama model list after pulls."
  ollama list || true
}

smoke_test_ollama_gpu() {
  [[ "$INSTALL_OLLAMA" == "1" ]] || return 0
  [[ "$SKIP_MODEL_SMOKE_TEST" == "0" ]] || { log "Skipping Ollama model GPU smoke test by request."; return 0; }
  [[ "$SKIP_GPU_VALIDATE" == "0" ]] || { log "Skipping Ollama model GPU smoke test because GPU validation is skipped."; return 0; }

  log "Running Ollama GPU smoke test with $GPU_TEST_MODEL."
  if ! ollama list | awk '{print $1}' | grep -qx "$GPU_TEST_MODEL"; then
    ollama pull "$GPU_TEST_MODEL"
  fi

  # Keep the model resident long enough for ollama ps to report processor placement.
  if command -v timeout >/dev/null 2>&1; then
    timeout 180s ollama run "$GPU_TEST_MODEL" "Reply with exactly OK." >/tmp/orchestrator_ollama_smoke.out 2>/tmp/orchestrator_ollama_smoke.err || true
  else
    ollama run "$GPU_TEST_MODEL" "Reply with exactly OK." >/tmp/orchestrator_ollama_smoke.out 2>/tmp/orchestrator_ollama_smoke.err || true
  fi

  sleep 2
  local ps_out
  ps_out="$(ollama ps 2>/dev/null || true)"
  printf '%s\n' "$ps_out"

  if printf '%s\n' "$ps_out" | grep -qi 'GPU'; then
    log "Ollama reports GPU usage."
    return 0
  fi

  warn "Ollama did not report GPU usage in ollama ps."
  warn "Recent Ollama logs:"
  journalctl -u ollama -n 80 --no-pager 2>/dev/null || true

  if [[ "$FORCE" == "1" ]]; then
    warn "Continuing because --force is set."
    return 0
  fi

  die "Ollama appears CPU-only. Stopping before OpenClaw so the default model is not bound to a broken runtime. Try rerunning with --force-cuda-library cuda_v12 or cuda_v13 only if logs show the CUDA runner is available but autodetection failed."
}

install_gpu_check_helper() {
  mkdir -p "$HOME/bin"
  cat > "$HOME/bin/ollama-gpu-check" <<'EOHELPER'
#!/usr/bin/env bash
set -euo pipefail
MODEL="${1:-qwen3:0.6b}"
if ! command -v ollama >/dev/null 2>&1; then
  echo "ollama not found" >&2
  exit 1
fi
if command -v nvidia-smi >/dev/null 2>&1; then
  nvidia-smi
elif [[ -x /usr/lib/wsl/lib/nvidia-smi ]]; then
  /usr/lib/wsl/lib/nvidia-smi
else
  echo "nvidia-smi not found" >&2
fi
ollama pull "$MODEL" >/dev/null
ollama run "$MODEL" "Reply exactly OK." >/tmp/ollama-gpu-check.out 2>/tmp/ollama-gpu-check.err || true
sleep 2
ollama ps
EOHELPER
  chmod +x "$HOME/bin/ollama-gpu-check"
}

install_openclaw() {
  [[ "$INSTALL_OPENCLAW" == "1" ]] || { log "Skipping OpenClaw install."; return 0; }

  log "Installing OpenClaw after Ollama/model setup."

  # Load nvm Node in this non-interactive shell.
  export NVM_DIR="$HOME/.nvm"
  if [[ -s "$NVM_DIR/nvm.sh" ]]; then
    # shellcheck disable=SC1091
    source "$NVM_DIR/nvm.sh"
    nvm use 24 >/dev/null || true
  fi

  # Current OpenClaw docs recommend the official installer. Use --no-onboard so this script
  # stays controlled unless the caller explicitly asked for onboarding.
  if curl -fsSL https://openclaw.ai/install.sh | bash -s -- --no-onboard; then
    log "OpenClaw installer completed."
  else
    warn "Official OpenClaw installer failed. Falling back to npm install -g openclaw@latest."
    npm install -g openclaw@latest
  fi

  if need_cmd openclaw; then
    openclaw --version || true
  else
    warn "openclaw command not found after install. Try opening a new shell, then run: openclaw --version"
  fi

  configure_openclaw_default_model || true

  if [[ "$OPENCLAW_ONBOARD" == "1" ]]; then
    log "Starting OpenClaw onboarding. This may ask for tokens/channel/provider configuration."
    openclaw onboard --install-daemon || {
      if [[ "$FORCE" == "1" ]]; then
        warn "OpenClaw onboarding failed but --force is set."
      else
        return 1
      fi
    }
    configure_openclaw_default_model || true
  else
    cat <<EOFMSG

OpenClaw installed.

When ready, run:

  openclaw onboard --install-daemon

The script attempted to set OpenClaw's default model to:

  ollama/$OPENCLAW_DEFAULT_MODEL

EOFMSG
  fi
}

configure_openclaw_default_model() {
  [[ "$INSTALL_OPENCLAW" == "1" ]] || return 0
  need_cmd openclaw || return 0

  log "Configuring OpenClaw default model: ollama/$OPENCLAW_DEFAULT_MODEL"

  # These keys match the current OpenClaw config shape used by prior ROC/OpenClaw setups.
  # If OpenClaw changes the schema, config set should fail safely and onboarding can set the model interactively.
  openclaw config set agents.defaults.model.primary "ollama/$OPENCLAW_DEFAULT_MODEL" || warn "Could not set agents.defaults.model.primary automatically. Set it during onboarding."
  openclaw config set agents.defaults.model.fallback "ollama/$OPENCLAW_FALLBACK_MODEL" || true
}

detect_project_path_in_archive() {
  local archive="$1"
  local listing
  listing="$(tar -tzf "$archive" 2>/dev/null | sed 's#^\./##')" || return 1

  # Repo-only archive: projects/main.py or projects/docs/...
  if printf '%s\n' "$listing" | grep -qE '^projects/(main.py|docs/|orchestrator/|tests/)'; then
    printf 'projects'
    return 0
  fi

  # Full old-home archive: home/roger/codex/projects/...
  local candidate
  candidate="$(printf '%s\n' "$listing" \
    | grep -E '(^|/)codex/projects/(main.py|docs/|orchestrator/|tests/)' \
    | head -n 1 \
    | sed -E 's#(.*codex/projects).*#\1#')" || true
  if [[ -n "$candidate" ]]; then
    printf '%s' "$candidate"
    return 0
  fi

  # Direct project archive: main.py, docs/, orchestrator/, tests/ at archive root.
  if printf '%s\n' "$listing" | grep -qE '^(main.py|docs/|orchestrator/|tests/)'; then
    printf '.'
    return 0
  fi

  return 1
}

restore_orchestrator() {
  [[ -n "$ORCH_ARCHIVE" ]] || { log "No --archive provided. Skipping Orchestrator restore."; return 0; }
  [[ -f "$ORCH_ARCHIVE" ]] || die "Archive not found: $ORCH_ARCHIVE"

  log "Restoring Orchestrator from archive: $ORCH_ARCHIVE"

  local project_path
  if ! project_path="$(detect_project_path_in_archive "$ORCH_ARCHIVE")"; then
    die "Could not find Orchestrator project subtree in archive. Expected projects/, codex/projects/, or home/roger/codex/projects/."
  fi

  log "Detected project subtree in archive: $project_path"

  local tmp
  tmp="$(mktemp -d)"
  mkdir -p "$CODEX_DIR" "$CODEX_DIR/projects"

  if [[ "$project_path" == "." ]]; then
    tar -xzf "$ORCH_ARCHIVE" -C "$tmp"
    rsync -a --delete "$tmp"/ "$CODEX_DIR/projects"/
  else
    tar -xzf "$ORCH_ARCHIVE" -C "$tmp" --wildcards "$project_path/*"
    rsync -a --delete "$tmp/$project_path"/ "$CODEX_DIR/projects"/
  fi

  rm -rf "$tmp"

  cd "$CODEX_DIR/projects"

  log "Cleaning generated/cache artifacts from restored project."
  find . -name '__pycache__' -type d -prune -exec rm -rf {} + 2>/dev/null || true
  find . -name '*.pyc' -delete 2>/dev/null || true
  find . -name '*:Zone.Identifier' -delete 2>/dev/null || true
  rm -rf .pytest_cache .mypy_cache 2>/dev/null || true

  log "Creating Orchestrator Python virtual environment."
  python3 -m venv .venv
  # shellcheck disable=SC1091
  source .venv/bin/activate
  python -m pip install --upgrade pip setuptools wheel

  if [[ -f requirements.txt ]]; then
    python -m pip install -r requirements.txt
  fi

  mkdir -p "$HOME/bin"
  cat > "$HOME/bin/orch" <<'EOORCH'
#!/usr/bin/env bash
set -e
cd "$HOME/codex/projects"
if [[ -f ".venv/bin/activate" ]]; then
  # shellcheck disable=SC1091
  source ".venv/bin/activate"
fi
exec python main.py "$@"
EOORCH
  chmod +x "$HOME/bin/orch"

  if [[ "$RUN_TESTS" == "1" && -d tests ]]; then
    log "Running Orchestrator tests."
    if ! python -m unittest discover -s tests; then
      warn "Tests failed. The project restored, but this environment may still need dependency/config work."
    fi
  fi

  log "Orchestrator restore complete."
  "$HOME/bin/orch" --help >/dev/null 2>&1 || warn "orch wrapper exists, but main.py --help did not complete."
}

configure_git_optional() {
  if [[ -n "${GIT_USER_NAME:-}" ]]; then
    git config --global user.name "$GIT_USER_NAME"
  fi
  if [[ -n "${GIT_USER_EMAIL:-}" ]]; then
    git config --global user.email "$GIT_USER_EMAIL"
  fi
  git config --global init.defaultBranch main >/dev/null 2>&1 || true
  git config --global pull.rebase false >/dev/null 2>&1 || true
}

print_summary() {
  log "Bootstrap summary"

  cat <<EOFMSG
User:                    $USER
Home:                    $HOME
Shell target:            $(command -v zsh 2>/dev/null || echo "zsh not found")
Current shell:           ${SHELL:-unknown}
Code directory:          $CODEX_DIR
OpenClaw install:        $INSTALL_OPENCLAW
OpenClaw default model:  ollama/$OPENCLAW_DEFAULT_MODEL
OpenClaw fallback model: ollama/$OPENCLAW_FALLBACK_MODEL
Ollama install:          $INSTALL_OLLAMA
Ollama model pack:       $MODEL_PACK
Ollama CUDA devices:     $(detect_cuda_visible_devices 2>/dev/null || echo unknown)
Archive restored:        ${ORCH_ARCHIVE:-none}

Versions:
EOFMSG

  {
    printf '  git:      '; git --version
    printf '  python:   '; python3 --version
    printf '  node:     '; node --version
    printf '  npm:      '; npm --version
    printf '  zsh:      '; zsh --version
    printf '  openclaw: '; openclaw --version 2>/dev/null || echo "not found"
    printf '  ollama:   '; ollama --version 2>/dev/null || echo "not found"
  } || true

  cat <<'EOFMSG'

Useful checks:
  ollama-gpu-check
  ollama ps
  ollama list
  journalctl -u ollama -n 120 --no-pager

Next actions:
  1. Close/reopen the WSL terminal so zsh becomes the default shell.
  2. In Windows Terminal, select a Nerd Font / MesloLGS NF for Powerlevel10k symbols.
  3. If you skipped onboarding, run:
       openclaw onboard --install-daemon
  4. If Orchestrator restored, test:
       orch status

EOFMSG
}

main() {
  ensure_not_root
  ensure_wsl
  ensure_systemd
  apt_install_base
  install_ohmyzsh_p10k
  install_node_nvm
  preflight_gpu
  install_ollama
  install_gpu_check_helper
  pull_ollama_models
  smoke_test_ollama_gpu
  install_openclaw
  restore_orchestrator
  configure_git_optional
  print_summary
}

main "$@"
