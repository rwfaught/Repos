#!/usr/bin/env bash
set -euo pipefail

distro_name="${1:?usage: watch_bootstrap.sh DISTRO_NAME RUN_TIMESTAMP [LINUX_USER]}"
run_timestamp="${2:?usage: watch_bootstrap.sh DISTRO_NAME RUN_TIMESTAMP [LINUX_USER]}"
linux_user="${3:-roger}"
log_root="/home/${linux_user}/openclaw_install/logs/${run_timestamp}"

wsl.exe --distribution "$distro_name" --user "$linux_user" -- bash -lc \
  "tail -n 80 -F '$log_root/runner.log' '$log_root/bootstrap.log' '$log_root/openclaw_npm_install.log' 2>/dev/null"
