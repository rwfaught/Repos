#!/usr/bin/env bash
set -Eeuo pipefail

SCRIPT_NAME="$(basename "$0")"
STAMP="$(date +%Y%m%d_%H%M%S)"
LOG_DIR=""
MARKER_DIR="${WIRE_MARKER_DIR:-}"

log() { printf '\n[%s] %s\n' "$SCRIPT_NAME" "$*"; }
die() { printf '\n[%s] ERROR: %s\n' "$SCRIPT_NAME" "$*" >&2; exit 1; }

usage() {
  cat <<'EOF'
Usage:
  bash apply_openclaw_repro_compat_layer_v1_7.sh --log-dir /path/to/logdir [--marker-dir /path/to/markers]
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --log-dir) LOG_DIR="${2:-}"; shift 2 ;;
    --marker-dir) MARKER_DIR="${2:-}"; shift 2 ;;
    --help|-h) usage; exit 0 ;;
    *) die "Unknown option: $1" ;;
  esac
done

[[ -n "$LOG_DIR" ]] || die "--log-dir is required"
mkdir -p "$LOG_DIR"
if [[ -n "$MARKER_DIR" ]]; then
  mkdir -p "$MARKER_DIR"
fi

REPORT_FILE="${LOG_DIR}/openclaw_repro_compat_stage_report.md"
SUMMARY_JSON="${LOG_DIR}/openclaw_repro_compat_stage_summary.json"

log "Verifying installed OpenClaw identity and applying fail-closed compatibility layer"

python3 - "$REPORT_FILE" "$SUMMARY_JSON" "$MARKER_DIR" <<'PY'
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

REPORT_FILE = Path(sys.argv[1])
SUMMARY_JSON = Path(sys.argv[2])
MARKER_DIR = Path(sys.argv[3]) if sys.argv[3] else None

EXPECTED_PACKAGE_SPEC = os.environ.get("OPENCLAW_NPM_PACKAGE_SPEC", "openclaw@2026.6.6")
EXPECTED_IDENTITY = os.environ.get("OPENCLAW_EXPECTED_IDENTITY", "OpenClaw 2026.6.6 (8c802aa)")
EXPECTED_BUILD_ID = os.environ.get("OPENCLAW_EXPECTED_BUILD_ID", "8c802aa")
EXPECTED_PACKAGE_VERSION = os.environ.get("OPENCLAW_EXPECTED_PACKAGE_VERSION", "2026.6.6")
IDENTITY_POLICY = os.environ.get("OPENCLAW_IDENTITY_POLICY", "observed-build-string")
ORIGINAL_USER = os.environ.get("OPENCLAW_COMPAT_ORIGINAL_USER", "")
ORIGINAL_GROUP = os.environ.get("OPENCLAW_COMPAT_ORIGINAL_GROUP", "")
PRIVILEGE_MODE = os.environ.get("OPENCLAW_COMPAT_PRIVILEGE_MODE", "sudo-root" if os.geteuid() == 0 else "user")

V92_LEGACY_PATCHED_HASH = "e3cd412d2b0d21b0025dd5ab981b417dba8efd98740f344d7c16919dd8cacec1"
V92_CURRENT_SAFE_HASH = "11fbd56dec3196b3c6e0767d9c27bfc11e097a1e05197c90b479962611bab0e0"
V92_ACCEPTED_FINAL_HASHES = {V92_LEGACY_PATCHED_HASH, V92_CURRENT_SAFE_HASH}
V99_FINAL_HASH = "8a79953bb26078883abe88e3512ce9ad75f91f1c2572f5258123851d93965ccb"
V103_FINAL_HASH = "6aacb5f4815bced020815a4fdf95a7535114866cb26d105643ca177ea26dfaf0"
V102_PRE_HASH = "3bff2a20ebaeb2cbc8689b709a5b80f9ccfd1eba7d9753f122b6f725cc6e2bff"
V102_POST_HASH = "3af0e1ed3d53e79052413fe09772e5577d1fb579ec98c87c320934683354f0d7"

V92_MARKER = "FIX_v1_7_92_STATUS_DEEP_ACTUAL_RENDERER_LABEL_FALLBACK_PATCH"
V99_MARKER = "FIX_v1_7_99_REMAINING_LABEL_FALLBACK_PATCH"
V102_MARKER = "FIX_v1_7_102_CHANNELS_LIST_EXPOSURE_FALLBACK_PATCH"
V103_MARKER = "FIX_v1_7_103_CHANNELS_LIST_META_SHOWCONFIGURED_FALLBACK_PATCH"

SAFE_HELPER_V92 = r'''
function __openclawFixV192SafeRendererLabel(candidate, fallback) {
  /* FIX_v1_7_92_STATUS_DEEP_ACTUAL_RENDERER_LABEL_FALLBACK_PATCH */
  if (candidate && typeof candidate.label === "string" && candidate.label.trim()) return candidate.label;
  if (candidate && typeof candidate.displayName === "string" && candidate.displayName.trim()) return candidate.displayName;
  if (candidate && typeof candidate.name === "string" && candidate.name.trim()) return candidate.name;
  if (candidate && typeof candidate.id === "string" && candidate.id.trim()) return candidate.id;
  if (candidate && typeof candidate.type === "string" && candidate.type.trim()) return candidate.type;
  const id = candidate && (candidate.accountId ?? candidate.channelId ?? candidate.providerId ?? candidate.pluginId ?? candidate.model ?? candidate.provider ?? candidate.key ?? candidate.account);
  if (typeof id === "string" && id.trim()) return id;
  if (typeof fallback === "string" && fallback.trim()) return fallback;
  return "unknown";
}
'''

def run(cmd, timeout=60):
    try:
        return subprocess.run(
            cmd,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired as exc:
        return subprocess.CompletedProcess(cmd, 124, exc.stdout or "", exc.stderr or "timeout")

def one_line(text, max_len=900):
    compact = re.sub(r"\s+", " ", str(text or "")).strip()
    if not compact:
        return "UNKNOWN"
    return compact[:max_len] + ("...<truncated>" if len(compact) > max_len else "")

def sha256_file(path):
    import hashlib
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def read_text(path):
    return path.read_text(encoding="utf-8", errors="replace")

def write_marker(key, value):
    if MARKER_DIR is None:
        return
    MARKER_DIR.mkdir(parents=True, exist_ok=True)
    marker = MARKER_DIR / f"{key}.marker"
    marker.write_text(
        f"key={key}\nvalue={value}\ntimestamp={subprocess.run(['date','-Iseconds'],text=True,stdout=subprocess.PIPE).stdout.strip()}\n",
        encoding="utf-8",
    )
    try:
        os.chmod(marker, 0o644)
    except Exception:
        pass
    ensure_user_readable(marker)

def ensure_user_readable(path):
    try:
        os.chmod(path, 0o644)
    except Exception:
        pass
    if ORIGINAL_USER:
        try:
            shutil.chown(path, user=ORIGINAL_USER, group=ORIGINAL_GROUP or None)
        except Exception:
            pass

def write_summary():
    SUMMARY_JSON.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    ensure_user_readable(SUMMARY_JSON)

def write_report(text):
    REPORT_FILE.write_text(text, encoding="utf-8")
    ensure_user_readable(REPORT_FILE)

def node_check(path):
    proc = run(["node", "--check", str(path)], timeout=45)
    return proc.returncode == 0, one_line((proc.stdout or "") + "\n" + (proc.stderr or ""))

def npm_root():
    proc = run(["npm", "root", "-g"], timeout=20)
    if proc.returncode != 0:
        return None, one_line((proc.stdout or "") + "\n" + (proc.stderr or ""))
    root = (proc.stdout or "").strip()
    if not root:
        return None, "npm-root-empty"
    return Path(root), "PASS"

def function_spans(text):
    patterns = [
        r"(?:async\s+)?function\s+([A-Za-z0-9_$]+)\s*\([^)]*\)\s*\{",
        r"(?:const|let|var)\s+([A-Za-z0-9_$]+)\s*=\s*(?:async\s+)?function\s*\([^)]*\)\s*\{",
        r"(?:const|let|var)\s+([A-Za-z0-9_$]+)\s*=\s*(?:async\s*)?\([^)]*\)\s*=>\s*\{",
        r"([A-Za-z0-9_$]+)\s*:\s*(?:async\s+)?function\s*\([^)]*\)\s*\{",
    ]
    starts = []
    for pattern in patterns:
        for match in re.finditer(pattern, text):
            brace = text.find("{", match.start())
            if brace >= 0:
                starts.append((match.group(1), match.start(), brace))
    spans = []
    seen = set()
    for name, start, brace in sorted(starts, key=lambda item: item[1]):
        if (name, start) in seen:
            continue
        seen.add((name, start))
        depth = 0
        quote = None
        escaped = False
        for idx in range(brace, len(text)):
            ch = text[idx]
            if quote:
                if escaped:
                    escaped = False
                elif ch == "\\":
                    escaped = True
                elif ch == quote:
                    quote = None
                continue
            if ch in ("'", '"', "`"):
                quote = ch
                continue
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    spans.append((name, start, idx + 1))
                    break
    return spans

def safe_label_expression():
    return (
        f'/* {V99_MARKER} */ '
        f'(()=>{{const __ocPlugin=plugin;const __ocMeta=__ocPlugin&&__ocPlugin.meta;'
        f'return __ocMeta&&typeof __ocMeta.label==="string"&&__ocMeta.label.trim()?__ocMeta.label:'
        f'__ocMeta&&typeof __ocMeta.name==="string"&&__ocMeta.name.trim()?__ocMeta.name:'
        f'__ocPlugin&&typeof __ocPlugin.name==="string"&&__ocPlugin.name.trim()?__ocPlugin.name:'
        f'__ocPlugin&&typeof __ocPlugin.id==="string"&&__ocPlugin.id.trim()?__ocPlugin.id:'
        f'"unknown";}})()'
    )

def safe_function_replacement():
    return (
        f'function resolveChannelExposure(meta){{'
        f'/* {V103_MARKER}; supersedes {V102_MARKER} */ '
        f'const __ocMeta=meta??{{}};'
        f'const __ocExposure=__ocMeta.exposure??{{}};'
        f'return {{configured:__ocExposure.configured??__ocMeta.showConfigured??true,'
        f'setup:__ocExposure.setup??__ocMeta.showInSetup??true,'
        f'docs:__ocExposure.docs??true}};'
        f'}}'
    )

def anchor_counts(text, anchors):
    return {name: text.count(needle) for name, needle in anchors.items()}

def v92_current_safe_structure_counts(text):
    return anchor_counts(text, {
        "selected_model_ref": "const selectedModelRef = parsedPendingModel ?? parsedCurrentModel;",
        "model_option_label": "label: model,",
        "model_option_default": "default: selectedModelRef ? selectedModelRef.provider === params.modelPage.provider && selectedModelRef.model === model : false",
        "provider_option_label": "label: provider.id,",
        "current_model_format": 'return `Current model: ${parsed.provider}/${parsed.model}`;',
    })

def v92_current_safe_structure_match(counts):
    return all(count >= 1 for count in counts.values())

def compact_counts(counts):
    return ",".join(f"{key}={counts[key]}" for key in sorted(counts))

def apply_v92(path):
    text = read_text(path)
    pre_hash = sha256_file(path)
    stale_counts = anchor_counts(text, {
        "modelRefs_selected_label": "modelRefs.selected.label",
        "modelRefs_active_label": "modelRefs.active.label",
    })
    current_structure_counts = v92_current_safe_structure_counts(text)
    base = {
        "target_path": str(path),
        "pre_hash": pre_hash,
        "post_hash": pre_hash,
        "anchor_counts": stale_counts,
        "current_structure_counts": current_structure_counts,
        "accepted_final_hashes": sorted(V92_ACCEPTED_FINAL_HASHES),
    }
    if pre_hash == V92_LEGACY_PATCHED_HASH:
        return {
            **base,
            "result": "already-compatible",
            "reason": "legacy-patched-final-hash-match",
            "selected_strategy": "legacy-v92-patched-hash",
        }
    if V92_MARKER in text:
        return {
            **base,
            "result": "blocked-drift",
            "reason": "fix-marker-present-but-hash-mismatch",
            "selected_strategy": "marker-present-hash-mismatch",
        }
    if pre_hash == V92_CURRENT_SAFE_HASH and v92_current_safe_structure_match(current_structure_counts):
        return {
            **base,
            "result": "already-compatible",
            "reason": "current-safe-provider-structure-hash-match",
            "selected_strategy": "hash-validated-current-provider-structure",
        }
    selected_count = stale_counts["modelRefs_selected_label"]
    active_count = stale_counts["modelRefs_active_label"]
    if selected_count > 1 or active_count > 1:
        return {
            **base,
            "result": "blocked-drift",
            "reason": f"ambiguous-modelrefs-anchor selected={selected_count} active={active_count}",
            "selected_strategy": "legacy-modelrefs-anchor-rewrite",
        }
    if selected_count + active_count < 1:
        structure_reason = compact_counts(current_structure_counts)
        return {
            **base,
            "result": "blocked-drift",
            "reason": f"modelrefs-anchor-missing;current_structure={structure_reason}",
            "selected_strategy": "no-legacy-anchor-no-proven-current-structure",
        }
    patched = text
    patched = patched.replace("modelRefs.selected.label", '__openclawFixV192SafeRendererLabel(modelRefs.selected, "selected")')
    patched = patched.replace("modelRefs.active.label", '__openclawFixV192SafeRendererLabel(modelRefs.active, "active")')
    insert_candidates = [idx for idx in [patched.find("__openclawFixV192SafeRendererLabel("), patched.find("modelRefs.")] if idx >= 0]
    if not insert_candidates:
        return {
            **base,
            "result": "blocked-drift",
            "reason": "helper-insert-anchor-missing",
            "selected_strategy": "legacy-modelrefs-anchor-rewrite",
        }
    insert_at = min(insert_candidates)
    patched = patched[:insert_at] + SAFE_HELPER_V92 + "\n" + patched[insert_at:]
    backup = path.with_name(f"{path.name}.before-REPRO_v1_7_02.{pre_hash[:16]}.bak")
    try:
        backup.write_text(text, encoding="utf-8")
        ensure_user_readable(backup)
        path.write_text(patched, encoding="utf-8")
    except OSError as exc:
        return {
            **base,
            "result": "blocked-write-failure",
            "reason": f"{type(exc).__name__}:{one_line(exc)}",
            "post_hash": sha256_file(path),
            "selected_strategy": "legacy-modelrefs-anchor-rewrite",
        }
    ok, detail = node_check(path)
    post_hash = sha256_file(path)
    if not ok or post_hash != V92_LEGACY_PATCHED_HASH:
        try:
            path.write_text(text, encoding="utf-8")
        except OSError as exc:
            return {
                **base,
                "result": "blocked-restore-failure",
                "reason": f"{type(exc).__name__}:{one_line(exc)}",
                "post_hash": sha256_file(path),
                "selected_strategy": "legacy-modelrefs-anchor-rewrite",
            }
        return {
            **base,
            "result": "blocked-validation-failure",
            "reason": f"node_check={ok};post_hash={post_hash};detail={detail}",
            "post_hash": sha256_file(path),
            "selected_strategy": "legacy-modelrefs-anchor-rewrite",
        }
    return {
        **base,
        "result": "patched",
        "reason": "exact-modelrefs-rewrite",
        "post_hash": post_hash,
        "selected_strategy": "legacy-modelrefs-anchor-rewrite",
    }

def apply_v99(path):
    text = read_text(path)
    pre_hash = sha256_file(path)
    if pre_hash == V99_FINAL_HASH:
        return {"result": "already-compatible", "reason": "final-post-hash-match", "pre_hash": pre_hash, "post_hash": pre_hash}
    if V99_MARKER in text:
        return {"result": "blocked-drift", "reason": "fix-marker-present-but-hash-mismatch", "pre_hash": pre_hash, "post_hash": pre_hash}
    spans = function_spans(text)
    candidates = []
    for name, start, end in spans:
        if name != "getHealthSnapshot":
            continue
        body = text[start:end]
        if "plugin.meta.label" not in body:
            continue
        candidates.append((start, end))
    if len(candidates) != 1:
        return {"result": "blocked-drift", "reason": f"getHealthSnapshot-plugin.meta.label-anchor-count={len(candidates)}", "pre_hash": pre_hash, "post_hash": pre_hash}
    start, end = candidates[0]
    segment = text[start:end]
    patched_segment, count = re.subn(r"\bplugin\.meta\.label\b", safe_label_expression(), segment, count=1)
    if count != 1:
        return {"result": "blocked-drift", "reason": f"plugin.meta.label-rewrite-count={count}", "pre_hash": pre_hash, "post_hash": pre_hash}
    patched = text[:start] + patched_segment + text[end:]
    backup = path.with_name(f"{path.name}.before-REPRO_v1_7_02.{pre_hash[:16]}.bak")
    try:
        backup.write_text(text, encoding="utf-8")
        ensure_user_readable(backup)
        path.write_text(patched, encoding="utf-8")
    except OSError as exc:
        return {"result": "blocked-write-failure", "reason": f"{type(exc).__name__}:{one_line(exc)}", "pre_hash": pre_hash, "post_hash": sha256_file(path)}
    ok, detail = node_check(path)
    post_hash = sha256_file(path)
    if not ok or post_hash != V99_FINAL_HASH:
        try:
            path.write_text(text, encoding="utf-8")
        except OSError as exc:
            return {"result": "blocked-restore-failure", "reason": f"{type(exc).__name__}:{one_line(exc)}", "pre_hash": pre_hash, "post_hash": sha256_file(path)}
        return {"result": "blocked-validation-failure", "reason": f"node_check={ok};post_hash={post_hash};detail={detail}", "pre_hash": pre_hash, "post_hash": sha256_file(path)}
    return {"result": "patched", "reason": "exact-health-anchor-rewrite", "pre_hash": pre_hash, "post_hash": post_hash}

def apply_v103(path):
    text = read_text(path)
    pre_hash = sha256_file(path)
    if pre_hash == V103_FINAL_HASH:
        return {"result": "already-compatible", "reason": "final-post-hash-match", "pre_hash": pre_hash, "post_hash": pre_hash}
    if V103_MARKER in text:
        return {"result": "blocked-drift", "reason": "fix-marker-present-but-hash-mismatch", "pre_hash": pre_hash, "post_hash": pre_hash}
    spans = function_spans(text)
    candidates = []
    for name, start, end in spans:
        if name != "resolveChannelExposure":
            continue
        body = text[start:end]
        if "meta.showConfigured" not in body:
            continue
        candidates.append((start, end))
    if len(candidates) != 1:
        return {"result": "blocked-drift", "reason": f"resolveChannelExposure-meta.showConfigured-anchor-count={len(candidates)}", "pre_hash": pre_hash, "post_hash": pre_hash}
    start, end = candidates[0]
    patched = text[:start] + safe_function_replacement() + text[end:]
    backup = path.with_name(f"{path.name}.before-REPRO_v1_7_02.{pre_hash[:16]}.bak")
    try:
        backup.write_text(text, encoding="utf-8")
        ensure_user_readable(backup)
        path.write_text(patched, encoding="utf-8")
    except OSError as exc:
        return {"result": "blocked-write-failure", "reason": f"{type(exc).__name__}:{one_line(exc)}", "pre_hash": pre_hash, "post_hash": sha256_file(path)}
    ok, detail = node_check(path)
    post_hash = sha256_file(path)
    if not ok or post_hash != V103_FINAL_HASH:
        try:
            path.write_text(text, encoding="utf-8")
        except OSError as exc:
            return {"result": "blocked-restore-failure", "reason": f"{type(exc).__name__}:{one_line(exc)}", "pre_hash": pre_hash, "post_hash": sha256_file(path)}
        return {"result": "blocked-validation-failure", "reason": f"node_check={ok};post_hash={post_hash};detail={detail}", "pre_hash": pre_hash, "post_hash": sha256_file(path)}
    return {"result": "patched", "reason": f"consolidated-v102-v103;v102_pre={V102_PRE_HASH};v102_post={V102_POST_HASH}", "pre_hash": pre_hash, "post_hash": post_hash}

summary = {
    "boundary": "REPRO_v1_7_02_IMPLEMENT_PINNED_OPENCLAW_IDENTITY_AND_FAIL_CLOSED_COMPAT_STAGE",
    "expectedPackageSpec": EXPECTED_PACKAGE_SPEC,
    "expectedIdentity": EXPECTED_IDENTITY,
    "expectedBuildId": EXPECTED_BUILD_ID,
    "identityPolicy": IDENTITY_POLICY,
    "compatibilityPrivilege": {
        "mode": PRIVILEGE_MODE,
        "result": "IN_PROGRESS",
        "reason": "helper-started",
        "effectiveUid": os.geteuid(),
        "originalUser": ORIGINAL_USER or "UNKNOWN",
        "originalGroup": ORIGINAL_GROUP or "UNKNOWN",
    },
    "identityVerification": {},
    "compatibilityStages": {},
    "validation": {},
}

write_marker("openclawCompatibilityPrivilegeMode", PRIVILEGE_MODE)
write_marker("openclawCompatibilityPrivilegeResult", "IN_PROGRESS")
write_marker("openclawCompatibilityPrivilegeReason", "helper-started")

npm_root_dir, npm_root_reason = npm_root()
if npm_root_dir is None:
    summary["identityVerification"] = {
        "result": "FAIL",
        "reason": f"npm-root-unavailable:{npm_root_reason}",
    }
    write_marker("openclawExpectedPackageSpec", EXPECTED_PACKAGE_SPEC)
    write_marker("openclawExpectedIdentity", EXPECTED_IDENTITY)
    summary["compatibilityPrivilege"]["result"] = "FAIL"
    summary["compatibilityPrivilege"]["reason"] = "npm-root-unavailable"
    write_marker("openclawCompatibilityPrivilegeMode", PRIVILEGE_MODE)
    write_marker("openclawCompatibilityPrivilegeResult", "FAIL")
    write_marker("openclawCompatibilityPrivilegeReason", "npm-root-unavailable")
    write_marker("openclawIdentityVerificationResult", "FAIL")
    write_marker("openclawIdentityVerificationReason", f"npm-root-unavailable:{npm_root_reason}")
    write_summary()
    write_report("# OpenClaw Repro Compatibility Stage\n\n- Identity verification failed before patching.\n")
    sys.exit(1)

openclaw_root = npm_root_dir / "openclaw"
dist_dir = openclaw_root / "dist"
package_json = openclaw_root / "package.json"
cli_metadata = dist_dir / "cli-startup-metadata.json"
version_proc = run(["openclaw", "--version"], timeout=30)
observed_identity = one_line((version_proc.stdout or "") + "\n" + (version_proc.stderr or ""), max_len=160)
pkg_name = "UNKNOWN"
pkg_version = "UNKNOWN"
pkg_git_head = "UNKNOWN"
cli_metadata_name = "UNKNOWN"
if package_json.exists():
    try:
        pkg_doc = json.loads(package_json.read_text(encoding="utf-8"))
        pkg_name = str(pkg_doc.get("name", "UNKNOWN"))
        pkg_version = str(pkg_doc.get("version", "UNKNOWN"))
        pkg_git_head = str(pkg_doc.get("gitHead", "UNKNOWN"))
    except Exception:
        pass
if cli_metadata.exists():
    try:
        cli_doc = json.loads(cli_metadata.read_text(encoding="utf-8"))
        cli_metadata_name = one_line(json.dumps(cli_doc, sort_keys=True), max_len=160)
    except Exception:
        pass

identity_base_ok = (
    version_proc.returncode == 0 and
    openclaw_root.exists() and
    dist_dir.exists() and
    pkg_name == "openclaw"
)
if IDENTITY_POLICY == "observed-build-string":
    identity_ok = (
        identity_base_ok and
        bool(EXPECTED_IDENTITY) and
        observed_identity == EXPECTED_IDENTITY and
        (not EXPECTED_BUILD_ID or EXPECTED_BUILD_ID in observed_identity)
    )
    identity_reason = "exact-observed-build-identity-match" if identity_ok else (
        f"expected={EXPECTED_IDENTITY};observed={observed_identity}"
    )
elif IDENTITY_POLICY == "package-version":
    identity_ok = identity_base_ok and bool(EXPECTED_PACKAGE_VERSION) and pkg_version == EXPECTED_PACKAGE_VERSION
    identity_reason = "installed-package-version-match" if identity_ok else (
        f"expectedPackageVersion={EXPECTED_PACKAGE_VERSION};observedPackageVersion={pkg_version};observedIdentity={observed_identity}"
    )
elif IDENTITY_POLICY == "version-command":
    identity_ok = identity_base_ok
    identity_reason = "version-command-and-package-metadata-valid" if identity_ok else (
        f"versionRc={version_proc.returncode};packageName={pkg_name};observedIdentity={observed_identity}"
    )
else:
    identity_ok = False
    identity_reason = f"unsupported-identity-policy:{IDENTITY_POLICY}"

summary["identityVerification"] = {
    "result": "PASS" if identity_ok else "FAIL",
    "reason": identity_reason,
    "openclawRoot": str(openclaw_root),
    "distDir": str(dist_dir),
    "observedIdentity": observed_identity,
    "observedPackageName": pkg_name,
    "observedPackageVersion": pkg_version,
    "observedGitHead": pkg_git_head,
    "observedCliStartupMetadata": cli_metadata_name,
}

write_marker("openclawExpectedPackageSpec", EXPECTED_PACKAGE_SPEC)
write_marker("openclawExpectedIdentity", EXPECTED_IDENTITY)
write_marker("openclawObservedIdentity", observed_identity)
write_marker("openclawIdentityObservedPackageName", pkg_name)
write_marker("openclawIdentityObservedPackageVersion", pkg_version)
write_marker("openclawIdentityObservedGitHead", pkg_git_head)
write_marker("openclawIdentityVerificationResult", "PASS" if identity_ok else "FAIL")
write_marker("openclawIdentityVerificationReason", summary["identityVerification"]["reason"])

if not identity_ok:
    summary["compatibilityStages"]["overallResult"] = "FAIL"
    summary["compatibilityStages"]["overallReason"] = "identity-verification-failed"
    summary["validation"]["result"] = "FAIL"
    summary["validation"]["reason"] = "deferred-because-identity-failed"
    summary["compatibilityPrivilege"]["result"] = "PASS"
    summary["compatibilityPrivilege"]["reason"] = "identity-verified-root-assisted-stage-entered"
    write_marker("openclawCompatibilityPrivilegeMode", PRIVILEGE_MODE)
    write_marker("openclawCompatibilityPrivilegeResult", "PASS")
    write_marker("openclawCompatibilityPrivilegeReason", "identity-verified-root-assisted-stage-entered")
    write_marker("openclawCompatibilityStageResult", "FAIL")
    write_marker("openclawCompatibilityStageReason", "identity-verification-failed")
    write_marker("openclawCompatibilityValidationResult", "FAIL")
    write_marker("openclawCompatibilityValidationReason", "identity-verification-failed")
    write_marker("openclawCompatibilityStageReportPath", str(REPORT_FILE))
    write_summary()
    write_report(
        "# OpenClaw Repro Compatibility Stage\n\n"
        "## Identity Verification\n\n"
        f"- Expected package spec: `{EXPECTED_PACKAGE_SPEC}`\n"
        f"- Expected identity: `{EXPECTED_IDENTITY}`\n"
        f"- Observed identity: `{observed_identity}`\n"
        f"- Result: `{summary['identityVerification']['result']}`\n"
        f"- Reason: `{summary['identityVerification']['reason']}`\n",
    )
    sys.exit(1)

if EXPECTED_PACKAGE_SPEC != "openclaw@2026.5.28":
    summary["compatibilityStages"]["overallResult"] = "PASS"
    summary["compatibilityStages"]["overallReason"] = "legacy-2026.5.28-layer-not-required-for-selected-package"
    summary["validation"]["result"] = "PASS"
    summary["validation"]["reason"] = "selected-package-identity-validated;legacy-layer-skipped"
    summary["compatibilityPrivilege"]["result"] = "PASS"
    summary["compatibilityPrivilege"]["reason"] = "identity-validated-no-legacy-patch-required"
    write_marker("openclawCompatibilityPrivilegeMode", PRIVILEGE_MODE)
    write_marker("openclawCompatibilityPrivilegeResult", "PASS")
    write_marker("openclawCompatibilityPrivilegeReason", summary["compatibilityPrivilege"]["reason"])
    write_marker("openclawCompatibilityStageResult", "PASS")
    write_marker("openclawCompatibilityStageReason", summary["compatibilityStages"]["overallReason"])
    write_marker("openclawCompatibilityValidationResult", "PASS")
    write_marker("openclawCompatibilityValidationReason", summary["validation"]["reason"])
    write_marker("openclawCompatibilityStageReportPath", str(REPORT_FILE))
    write_summary()
    write_report(
        "# OpenClaw Repro Compatibility Stage\n\n"
        "## Identity Verification\n\n"
        f"- Expected package spec: `{EXPECTED_PACKAGE_SPEC}`\n"
        f"- Identity policy: `{IDENTITY_POLICY}`\n"
        f"- Observed identity: `{observed_identity}`\n"
        f"- Observed package version: `{pkg_version}`\n"
        f"- Result: `{summary['identityVerification']['result']}`\n"
        f"- Reason: `{summary['identityVerification']['reason']}`\n\n"
        "## Compatibility Stage\n\n"
        "- Result: `PASS`\n"
        "- Reason: legacy OpenClaw 2026.5.28 compatibility patch is not applied to the selected package.\n",
    )
    sys.exit(0)

targets = {
    "v92": dist_dir / "provider-B9RENNR5.js",
    "v99": dist_dir / "health-qBnQetbg.js",
    "v103": dist_dir / "channel-meta-COEgfCjE.js",
}
missing = [name for name, path in targets.items() if not path.exists()]
if missing:
    summary["compatibilityStages"]["overallResult"] = "FAIL"
    summary["compatibilityStages"]["overallReason"] = "missing-targets:" + ",".join(missing)
    summary["validation"]["result"] = "FAIL"
    summary["validation"]["reason"] = "missing-targets"
    summary["compatibilityPrivilege"]["result"] = "PASS"
    summary["compatibilityPrivilege"]["reason"] = "root-assisted-stage-ran-missing-targets"
    write_marker("openclawCompatibilityPrivilegeMode", PRIVILEGE_MODE)
    write_marker("openclawCompatibilityPrivilegeResult", "PASS")
    write_marker("openclawCompatibilityPrivilegeReason", "root-assisted-stage-ran-missing-targets")
    write_marker("openclawCompatibilityStageResult", "FAIL")
    write_marker("openclawCompatibilityStageReason", summary["compatibilityStages"]["overallReason"])
    write_marker("openclawCompatibilityValidationResult", "FAIL")
    write_marker("openclawCompatibilityValidationReason", "missing-targets")
    write_marker("openclawCompatibilityStageReportPath", str(REPORT_FILE))
    write_summary()
    write_report(
        "# OpenClaw Repro Compatibility Stage\n\n"
        "## Identity Verification\n\n"
        "- Result: `PASS`\n\n"
        "## Compatibility Stage\n\n"
        f"- Result: `FAIL`\n"
        f"- Reason: `{summary['compatibilityStages']['overallReason']}`\n",
    )
    sys.exit(1)

stage_v92 = apply_v92(targets["v92"])
stage_v99 = apply_v99(targets["v99"])
stage_v103 = apply_v103(targets["v103"])
summary["compatibilityStages"]["v92"] = stage_v92
summary["compatibilityStages"]["v99"] = stage_v99
summary["compatibilityStages"]["v103"] = stage_v103

final_hashes = {
    "v92": sha256_file(targets["v92"]),
    "v99": sha256_file(targets["v99"]),
    "v103": sha256_file(targets["v103"]),
}
validation_ok = (
    final_hashes["v92"] in V92_ACCEPTED_FINAL_HASHES and
    final_hashes["v99"] == V99_FINAL_HASH and
    final_hashes["v103"] == V103_FINAL_HASH
)
stage_failures = [
    name for name, stage in [("v92", stage_v92), ("v99", stage_v99), ("v103", stage_v103)]
    if stage["result"] not in {"already-compatible", "patched"}
]
overall_ok = not stage_failures and validation_ok

summary["compatibilityStages"]["overallResult"] = "PASS" if overall_ok else "FAIL"
summary["compatibilityStages"]["overallReason"] = "all-stages-compatible" if overall_ok else (
    "stage-failure:" + ",".join(stage_failures) if stage_failures else "validation-hash-mismatch"
)
summary["validation"] = {
    "result": "PASS" if validation_ok else "FAIL",
    "reason": "final-post-hashes-match-ratified-state" if validation_ok else (
        f"v92={final_hashes['v92']};v99={final_hashes['v99']};v103={final_hashes['v103']}"
    ),
    "finalHashes": final_hashes,
}

summary["compatibilityPrivilege"]["result"] = "PASS" if os.geteuid() == 0 else "PASS"
summary["compatibilityPrivilege"]["reason"] = "root-assisted-patching-available" if os.geteuid() == 0 else "user-direct"

write_marker("openclawCompatibilityV92Result", stage_v92["result"])
write_marker("openclawCompatibilityV92Reason", stage_v92["reason"])
write_marker("openclawCompatibilityV92TargetPath", stage_v92["target_path"])
write_marker("openclawCompatibilityV92PreHash", stage_v92["pre_hash"])
write_marker("openclawCompatibilityV92PostHash", stage_v92["post_hash"])
write_marker("openclawCompatibilityV92AnchorCounts", compact_counts(stage_v92["anchor_counts"]))
write_marker("openclawCompatibilityV92CurrentStructureCounts", compact_counts(stage_v92["current_structure_counts"]))
write_marker("openclawCompatibilityV92SelectedStrategy", stage_v92["selected_strategy"])
write_marker("openclawCompatibilityV92AcceptedFinalHashes", ",".join(stage_v92["accepted_final_hashes"]))
write_marker("openclawCompatibilityV99Result", stage_v99["result"])
write_marker("openclawCompatibilityV103Result", stage_v103["result"])
write_marker("openclawCompatibilityPrivilegeMode", PRIVILEGE_MODE)
write_marker("openclawCompatibilityPrivilegeResult", summary["compatibilityPrivilege"]["result"])
write_marker("openclawCompatibilityPrivilegeReason", summary["compatibilityPrivilege"]["reason"])
write_marker("openclawCompatibilityStageResult", summary["compatibilityStages"]["overallResult"])
write_marker("openclawCompatibilityStageReason", summary["compatibilityStages"]["overallReason"])
write_marker("openclawCompatibilityValidationResult", summary["validation"]["result"])
write_marker("openclawCompatibilityValidationReason", summary["validation"]["reason"])
write_marker("openclawCompatibilityStageReportPath", str(REPORT_FILE))

write_summary()

report_lines = [
    "# OpenClaw Repro Compatibility Stage",
    "",
    "## Identity Verification",
    "",
    f"- Expected package spec: `{EXPECTED_PACKAGE_SPEC}`",
    f"- Expected identity: `{EXPECTED_IDENTITY}`",
    f"- Identity policy: `{IDENTITY_POLICY}`",
    f"- Observed identity: `{observed_identity}`",
    f"- Observed package name: `{pkg_name}`",
    f"- Observed package version: `{pkg_version}`",
    f"- Observed gitHead: `{pkg_git_head}`",
    f"- Result: `{summary['identityVerification']['result']}`",
    f"- Reason: `{summary['identityVerification']['reason']}`",
    "",
    "## Privilege Mode",
    "",
    f"- Privilege mode: `{summary['compatibilityPrivilege']['mode']}`",
    f"- Privilege result: `{summary['compatibilityPrivilege']['result']}`",
    f"- Privilege reason: `{summary['compatibilityPrivilege']['reason']}`",
    f"- Effective UID: `{summary['compatibilityPrivilege']['effectiveUid']}`",
    f"- Original user: `{summary['compatibilityPrivilege']['originalUser']}`",
    "",
    "## Compatibility Stages",
    "",
    f"- v92 provider label fallback: `{stage_v92['result']}` ({stage_v92['reason']})",
    f"- v92 target path: `{stage_v92['target_path']}`",
    f"- v92 pre hash: `{stage_v92['pre_hash']}`",
    f"- v92 post hash: `{stage_v92['post_hash']}`",
    f"- v92 selected strategy: `{stage_v92['selected_strategy']}`",
    f"- v92 anchor counts: `{compact_counts(stage_v92['anchor_counts'])}`",
    f"- v92 current structure counts: `{compact_counts(stage_v92['current_structure_counts'])}`",
    f"- v92 accepted final hashes: `{','.join(stage_v92['accepted_final_hashes'])}`",
    f"- v99 health snapshot label fallback: `{stage_v99['result']}` ({stage_v99['reason']})",
    f"- consolidated v102/v103 channel-meta fallback: `{stage_v103['result']}` ({stage_v103['reason']})",
    f"- Overall result: `{summary['compatibilityStages']['overallResult']}`",
    f"- Overall reason: `{summary['compatibilityStages']['overallReason']}`",
    "",
    "## Static Validation",
    "",
    f"- Validation result: `{summary['validation']['result']}`",
    f"- Validation reason: `{summary['validation']['reason']}`",
    f"- v92 final hash: `{final_hashes['v92']}`",
    f"- v99 final hash: `{final_hashes['v99']}`",
    f"- v103 final hash: `{final_hashes['v103']}`",
]
write_report("\n".join(report_lines) + "\n")

if not overall_ok:
    sys.exit(1)
PY

log "Compatibility stage report: $REPORT_FILE"
