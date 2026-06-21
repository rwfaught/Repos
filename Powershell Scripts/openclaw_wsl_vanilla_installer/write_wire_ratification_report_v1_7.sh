#!/usr/bin/env bash
set -Eeuo pipefail

RUN_DIR=""
CONFIG_PATH=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --run-dir) RUN_DIR="${2:-}"; shift 2 ;;
    --config) CONFIG_PATH="${2:-}"; shift 2 ;;
    --help|-h) exit 0 ;;
    *) echo "Unknown option: $1" >&2; exit 1 ;;
  esac
done

[[ -n "$RUN_DIR" ]] || { echo "--run-dir required" >&2; exit 1; }
[[ -d "$RUN_DIR/wire_status" ]] || { echo "Missing wire_status dir" >&2; exit 1; }
MARKER_DIR="$RUN_DIR/wire_markers"

status_val(){ local f="$RUN_DIR/wire_status/$1.status"; [[ -f "$f" ]] && sed -n 's/^status=//p' "$f" || echo "UNKNOWN"; }
marker_val(){ local f="$MARKER_DIR/$1.marker"; [[ -f "$f" ]] && sed -n 's/^value=//p' "$f" | head -n1 || echo "UNKNOWN"; }

bootstrap="$(status_val bootstrap)"
baseline="$(status_val baseline_verifier)"
dash="$(status_val dashboard_verifier)"
dcfg="$(status_val discord_config)"
dver="$(status_val discord_verifier)"
runtime_ready="$(status_val runtime_readiness)"
optional="$(status_val optional_model_verifier)"
dashboard_prompt_sent="$(marker_val dashboard_prompt_sent)"
dashboard_transport_proof="$(marker_val dashboardTransportProof)"
dashboard_model_loaded_proof="$(marker_val dashboardModelLoadedProof)"
dashboard_gpu_context_proof="$(marker_val dashboardGpuContextProof)"
dashboard_exact_response_proof="$(marker_val dashboardExactResponseProof)"
dashboard_verifier_result="$(marker_val dashboardVerifierResult)"
dashboard_failure_reason="$(marker_val dashboardFailureReason)"
dashboard_auth_probe_noise="$(marker_val dashboardAuthProbeNoise)"
dashboard_auth_probe_noise_lines_count="$(marker_val dashboardAuthProbeNoiseLinesCount)"
dashboard_device_probe_noise="$(marker_val dashboardDeviceProbeNoise)"
dashboard_device_probe_noise_lines_count="$(marker_val dashboardDeviceProbeNoiseLinesCount)"
dashboard_auth_url_copied="$(marker_val dashboardAuthUrlCopied)"
dashboard_open_requested="$(marker_val dashboardOpenRequested)"
dashboard_auto_open_result="$(marker_val dashboardAutoOpenResult)"
dashboard_auth_helper_result="$(marker_val dashboardAuthHelperResult)"
dashboard_material_failure_lines_count="$(marker_val dashboardMaterialFailureLinesCount)"
dashboard_compaction_diagnostic_noise="$(marker_val dashboardCompactionDiagnosticNoise)"
dashboard_compaction_diagnostic_lines_count="$(marker_val dashboardCompactionDiagnosticLinesCount)"
dashboard_prompt_surfaced="$(marker_val dashboard_prompt_surfaced)"
discord_token_provided="$(marker_val discord_token_provided)"
discord_token_prompt_surfaced="$(marker_val discord_token_prompt_surfaced)"
discord_token_source="$(marker_val discordTokenSource)"
discord_token_file_configured="$(marker_val discordTokenFileConfigured)"
discord_token_file_present="$(marker_val discordTokenFilePresent)"
discord_token_file_non_empty="$(marker_val discordTokenFileNonEmpty)"
discord_token_read_result="$(marker_val discordTokenReadResult)"
discord_token_value_logged="$(marker_val discordTokenValueLogged)"
discord_runtime_secret_handling="$(marker_val discordRuntimeSecretHandling)"
discord_runtime_secret_persistence="$(marker_val discordRuntimeSecretPersistence)"
discord_token_durable_exposure="$(marker_val discordTokenDurableExposure)"
discord_token_install_config_value_stored="$(marker_val discordTokenInstallConfigValueStored)"
discord_pairing_approved="$(marker_val discord_pairing_approved)"
discord_pairing_prompt_surfaced="$(marker_val discord_pairing_prompt_surfaced)"
discord_manual_proof_prompt_surfaced="$(marker_val discord_manual_proof_prompt_surfaced)"
discord_prompt_sent="$(marker_val discord_prompt_sent)"
discord_refresh_token_requested="$(marker_val discord_refresh_token_requested)"
discord_config_model_guard_result="$(marker_val discordConfigModelGuardResult)"
discord_config_expected_primary_model="$(marker_val discordConfigExpectedPrimaryModel)"
discord_config_model_tier="$(marker_val discordConfigModelTier)"
discord_config_failure_reason="$(marker_val discordConfigFailureReason)"
discord_external_plugin_install_required="$(marker_val discordExternalPluginInstallRequired)"
discord_external_plugin_install_attempted="$(marker_val discordExternalPluginInstallAttempted)"
discord_external_plugin_install_result="$(marker_val discordExternalPluginInstallResult)"
openclaw_readonly_external_plugins_patch_result="$(marker_val openclawReadonlyExternalPluginsPatchResult)"
openclaw_readonly_external_plugins_patch_proof="$(marker_val openclawReadonlyExternalPluginsPatchProof)"
discord_native_channel_add_attempted="$(marker_val discordNativeChannelAddAttempted)"
discord_native_channel_add_methods_tried="$(marker_val discordNativeChannelAddMethodsTried)"
discord_native_channel_add_final_method="$(marker_val discordNativeChannelAddFinalMethod)"
discord_native_channel_add_command_result="$(marker_val discordNativeChannelAddCommandResult)"
discord_native_channel_add_state_result="$(marker_val discordNativeChannelAddStateResult)"
discord_native_channel_add_result="$(marker_val discordNativeChannelAddResult)"
discord_native_channel_add_failure_reason="$(marker_val discordNativeChannelAddFailureReason)"
discord_setup_method="$(marker_val discordSetupMethod)"
discord_secretref_config_attempted="$(marker_val discordSecretRefConfigAttempted)"
discord_secretref_config_result="$(marker_val discordSecretRefConfigResult)"
discord_secretref_config_failure_reason="$(marker_val discordSecretRefConfigFailureReason)"
discord_enabled_config_result="$(marker_val discordEnabledConfigResult)"
discord_account_scoped_config_attempted="$(marker_val discordAccountScopedConfigAttempted)"
discord_account_scoped_config_result="$(marker_val discordAccountScopedConfigResult)"
discord_account_scoped_config_failure_reason="$(marker_val discordAccountScopedConfigFailureReason)"
discord_account_scoped_token_result="$(marker_val discordAccountScopedTokenResult)"
discord_account_scoped_enabled_result="$(marker_val discordAccountScopedEnabledResult)"
discord_env_only_implicit_default_attempted="$(marker_val discordEnvOnlyImplicitDefaultAttempted)"
discord_env_only_implicit_default_result="$(marker_val discordEnvOnlyImplicitDefaultResult)"
discord_env_only_implicit_default_failure_reason="$(marker_val discordEnvOnlyImplicitDefaultFailureReason)"
discord_plugin_entry_gate_attempted="$(marker_val discordPluginEntryGateAttempted)"
discord_plugin_entry_gate_result="$(marker_val discordPluginEntryGateResult)"
discord_plugin_entry_gate_failure_reason="$(marker_val discordPluginEntryGateFailureReason)"
discord_plugin_entry_keys="$(marker_val discordPluginEntryKeys)"
discord_plugin_entry_discord_present="$(marker_val discordPluginEntryDiscordPresent)"
discord_plugin_entry_discord_enabled="$(marker_val discordPluginEntryDiscordEnabled)"
discord_plugin_entry_config_validate_result="$(marker_val discordPluginEntryConfigValidateResult)"
discord_deep_status_gate_result="$(marker_val discordDeepStatusGateResult)"
discord_deep_status_gate_failure_reason="$(marker_val discordDeepStatusGateFailureReason)"
discord_deep_status_has_discord="$(marker_val discordDeepStatusHasDiscord)"
discord_deep_status_no_channels_configured="$(marker_val discordDeepStatusNoChannelsConfigured)"
discord_top_level_token_removed_for_env_only="$(marker_val discordTopLevelTokenRemovedForEnvOnly)"
discord_account_scoped_token_removed_for_env_only="$(marker_val discordAccountScopedTokenRemovedForEnvOnly)"
discord_script_env_token_present="$(marker_val discordScriptEnvTokenPresent)"
discord_script_env_token_length="$(marker_val discordScriptEnvTokenLength)"
discord_systemd_env_token_present="$(marker_val discordSystemdEnvTokenPresent)"
discord_systemd_env_token_length="$(marker_val discordSystemdEnvTokenLength)"
discord_gateway_env_token_present="$(marker_val discordGatewayEnvTokenPresent)"
discord_gateway_env_token_length="$(marker_val discordGatewayEnvTokenLength)"
discord_cli_env_injected_for_status="$(marker_val discordCliEnvInjectedForStatus)"
discord_cli_env_injected_accounts_json_count="$(marker_val discordCliEnvInjectedAccountsJsonCount)"
discord_cli_env_injected_line="$(marker_val discordCliEnvInjectedLine)"
discord_inactive_surface_warning_seen="$(marker_val discordInactiveSurfaceWarningSeen)"
discord_accounts_json_count="$(marker_val discordAccountsJsonCount)"
discord_loaded_adapter_proof_attempted="$(marker_val discordLoadedAdapterProofAttempted)"
discord_loaded_adapter_proof_result="$(marker_val discordLoadedAdapterProofResult)"
discord_loaded_adapter_proof_failure_reason="$(marker_val discordLoadedAdapterProofFailureReason)"
discord_loaded_adapter_ids_env_only="$(marker_val discordLoadedAdapterIdsEnvOnly)"
discord_loaded_adapter_default_account_id_env_only="$(marker_val discordLoadedAdapterDefaultAccountIdEnvOnly)"
discord_loaded_adapter_configured_env_only="$(marker_val discordLoadedAdapterConfiguredEnvOnly)"
discord_loaded_adapter_token_source_env_only="$(marker_val discordLoadedAdapterTokenSourceEnvOnly)"
discord_loaded_adapter_token_status_env_only="$(marker_val discordLoadedAdapterTokenStatusEnvOnly)"
discord_loaded_adapter_token_length_env_only="$(marker_val discordLoadedAdapterTokenLengthEnvOnly)"
discord_loaded_adapter_ids_explicit_default="$(marker_val discordLoadedAdapterIdsExplicitDefault)"
discord_loaded_adapter_configured_explicit_default="$(marker_val discordLoadedAdapterConfiguredExplicitDefault)"
discord_public_status_accounts_count="$(marker_val discordPublicStatusAccountsCount)"
discord_status_layer_lazy_plugin_bug_suspected="$(marker_val discordStatusLayerLazyPluginBugSuspected)"
discord_failure_class="$(marker_val discordFailureClass)"
discord_rollback_decision="$(marker_val discordRollbackDecision)"
discord_rollback_reason="$(marker_val discordRollbackReason)"
discord_env_only_config_preserved="$(marker_val discordEnvOnlyConfigPreserved)"
discord_known_bad_secretref_restore_skipped="$(marker_val discordKnownBadSecretRefRestoreSkipped)"
discord_post_failure_config_has_top_level_token="$(marker_val discordPostFailureConfigHasTopLevelToken)"
discord_post_failure_config_shape="$(marker_val discordPostFailureConfigShape)"
discord_gateway_provider_startup_seen="$(marker_val discordGatewayProviderStartupSeen)"
discord_gateway_provider_startup_pattern="$(marker_val discordGatewayProviderStartupPattern)"
discord_gateway_generic_ready_only="$(marker_val discordGatewayGenericReadyOnly)"
discord_gateway_provider_startup_detection_result="$(marker_val discordGatewayProviderStartupDetectionResult)"
discord_gateway_provider_startup_matched_line="$(marker_val discordGatewayProviderStartupMatchedLine)"
discord_gateway_provider_startup_matched_line_sha256="$(marker_val discordGatewayProviderStartupMatchedLineSha256)"
discord_runtime_may_still_work="$(marker_val discordRuntimeMayStillWork)"
discord_plugin_installed="$(marker_val discordPluginInstalled)"
discord_env_token_present="$(marker_val discordEnvTokenPresent)"
discord_adapter_env_configured_plausible="$(marker_val discordAdapterEnvConfiguredPlausible)"
discord_public_account_recognized="$(marker_val discordPublicAccountRecognized)"
discord_public_status_configured_enabled="$(marker_val discordPublicStatusConfiguredEnabled)"
discord_provider_startup_observed="$(marker_val discordProviderStartupObserved)"
discord_message_proof_completed="$(marker_val discordMessageProofCompleted)"
discord_verifier_allowed="$(marker_val discordVerifierAllowed)"
discord_manual_message_proof="$(marker_val discordManualMessageProof)"
discord_transport_proof="$(marker_val discordTransportProof)"
post_install_runtime_readiness="$(marker_val postInstallRuntimeReadiness)"
final_gateway_status="$(marker_val finalGatewayStatus)"
final_discord_status="$(marker_val finalDiscordStatus)"
discord_public_account_recognition_source="$(marker_val discordPublicAccountRecognitionSource)"
discord_repair_attempted="$(marker_val discordRepairAttempted)"
discord_repair_method="$(marker_val discordRepairMethod)"
discord_repair_result="$(marker_val discordRepairResult)"
discord_repair_failure_reason="$(marker_val discordRepairFailureReason)"
discord_line_before_native_add="$(marker_val discordLineBeforeNativeAdd)"
discord_line_after_use_env="$(marker_val discordLineAfterUseEnv)"
discord_line_after_token_file="$(marker_val discordLineAfterTokenFile)"
discord_line_after_bot_token="$(marker_val discordLineAfterBotToken)"
discord_line_after_native_add="$(marker_val discordLineAfterNativeAdd)"
discord_line_after_secretref_config="$(marker_val discordLineAfterSecretRefConfig)"
discord_line_after_account_scoped_config="$(marker_val discordLineAfterAccountScopedConfig)"
discord_line_after_env_only_implicit_default="$(marker_val discordLineAfterEnvOnlyImplicitDefault)"
discord_channel_state_parser_result="$(marker_val discordChannelStateParserResult)"
discord_channel_state_before_repair="$(marker_val discordChannelStateBeforeRepair)"
discord_channel_state_after_repair="$(marker_val discordChannelStateAfterRepair)"
discord_channel_installed="$(marker_val discordChannelInstalled)"
discord_channel_configured="$(marker_val discordChannelConfigured)"
discord_channel_config_result="$(marker_val discordChannelConfigResult)"
discord_channel_enabled="$(marker_val discordChannelEnabled)"
discord_channel_activation_result="$(marker_val discordChannelActivationResult)"
discord_config_result="$(marker_val discordConfigResult)"
shell_customization_attempted="$(marker_val shellCustomizationAttempted)"
shell_customization_result="$(marker_val shellCustomizationResult)"
shell_customization_failure_reason="$(marker_val shellCustomizationFailureReason)"
openclaw_npm_install_attempted="$(marker_val openclawNpmInstallAttempted)"
openclaw_npm_install_result="$(marker_val openclawNpmInstallResult)"
openclaw_npm_install_attempts="$(marker_val openclawNpmInstallAttempts)"
openclaw_npm_install_failure_reason="$(marker_val openclawNpmInstallFailureReason)"
openclaw_npm_install_duration_seconds="$(marker_val openclawNpmInstallDurationSeconds)"
install_terminal_result="$(marker_val installTerminalResult)"
install_failure_reason="$(marker_val installFailureReason)"
runtime_proof_disposition="$(marker_val runtimeProofDisposition)"
linux_path_hardening_result="$(marker_val linuxPathHardeningResult)"
linux_path_windows_segments_present="$(marker_val linuxPathWindowsSegmentsPresent)"
linux_path_hardening_phase="$(marker_val linuxPathHardeningPhase)"
append_windows_path_policy_marker="$(marker_val appendWindowsPathPolicy)"
linux_node_resolution_initial="$(marker_val linuxNodeResolutionInitial)"
linux_npm_resolution_initial="$(marker_val linuxNpmResolutionInitial)"
openclaw_resolution_initial="$(marker_val openclawResolutionInitial)"
linux_node_resolution_before_node_install="$(marker_val linuxNodeResolutionBeforeNodeInstall)"
linux_npm_resolution_before_node_install="$(marker_val linuxNpmResolutionBeforeNodeInstall)"
openclaw_resolution_before_node_install="$(marker_val openclawResolutionBeforeNodeInstall)"
linux_node_resolution_after_node_install="$(marker_val linuxNodeResolutionAfterNodeInstall)"
linux_npm_resolution_after_node_install="$(marker_val linuxNpmResolutionAfterNodeInstall)"
linux_node_npm_gate_result="$(marker_val linuxNodeNpmGateResult)"
linux_node_resolution_before_openclaw_install="$(marker_val linuxNodeResolutionBeforeOpenClawInstall)"
linux_npm_resolution_before_openclaw_install="$(marker_val linuxNpmResolutionBeforeOpenClawInstall)"
openclaw_resolution_before_openclaw_install="$(marker_val openclawResolutionBeforeOpenClawInstall)"
openclaw_resolution_after_openclaw_install="$(marker_val openclawResolutionAfterOpenClawInstall)"
openclaw_command_resolution_guard_result="$(marker_val openclawCommandResolutionGuardResult)"
openclaw_expected_package_spec="$(marker_val openclawExpectedPackageSpec)"
openclaw_expected_identity="$(marker_val openclawExpectedIdentity)"
openclaw_observed_identity="$(marker_val openclawObservedIdentity)"
openclaw_identity_verification_result="$(marker_val openclawIdentityVerificationResult)"
openclaw_identity_verification_reason="$(marker_val openclawIdentityVerificationReason)"
openclaw_identity_observed_package_name="$(marker_val openclawIdentityObservedPackageName)"
openclaw_identity_observed_package_version="$(marker_val openclawIdentityObservedPackageVersion)"
openclaw_identity_observed_git_head="$(marker_val openclawIdentityObservedGitHead)"
openclaw_compatibility_privilege_mode="$(marker_val openclawCompatibilityPrivilegeMode)"
openclaw_compatibility_privilege_result="$(marker_val openclawCompatibilityPrivilegeResult)"
openclaw_compatibility_privilege_reason="$(marker_val openclawCompatibilityPrivilegeReason)"
openclaw_compatibility_v92_result="$(marker_val openclawCompatibilityV92Result)"
openclaw_compatibility_v92_reason="$(marker_val openclawCompatibilityV92Reason)"
openclaw_compatibility_v92_target_path="$(marker_val openclawCompatibilityV92TargetPath)"
openclaw_compatibility_v92_pre_hash="$(marker_val openclawCompatibilityV92PreHash)"
openclaw_compatibility_v92_post_hash="$(marker_val openclawCompatibilityV92PostHash)"
openclaw_compatibility_v92_anchor_counts="$(marker_val openclawCompatibilityV92AnchorCounts)"
openclaw_compatibility_v92_current_structure_counts="$(marker_val openclawCompatibilityV92CurrentStructureCounts)"
openclaw_compatibility_v92_selected_strategy="$(marker_val openclawCompatibilityV92SelectedStrategy)"
openclaw_compatibility_v92_accepted_final_hashes="$(marker_val openclawCompatibilityV92AcceptedFinalHashes)"
openclaw_compatibility_v99_result="$(marker_val openclawCompatibilityV99Result)"
openclaw_compatibility_v103_result="$(marker_val openclawCompatibilityV103Result)"
openclaw_compatibility_stage_result="$(marker_val openclawCompatibilityStageResult)"
openclaw_compatibility_stage_reason="$(marker_val openclawCompatibilityStageReason)"
openclaw_compatibility_validation_result="$(marker_val openclawCompatibilityValidationResult)"
openclaw_compatibility_validation_reason="$(marker_val openclawCompatibilityValidationReason)"
openclaw_compatibility_stage_report_path="$(marker_val openclawCompatibilityStageReportPath)"
ollama_model_tier="$(marker_val ollamaModelTier)"
ollama_model_pull_attempted="$(marker_val ollamaModelPullAttempted)"
ollama_model_pull_result="$(marker_val ollamaModelPullResult)"
ollama_model_pull_failure_reason="$(marker_val ollamaModelPullFailureReason)"
ollama_model_pull_attempts="$(marker_val ollamaModelPullAttempts)"
preferred_safe_model_tier_result="$(marker_val preferredSafeModelTierResult)"
minimal_wire_model_result="$(marker_val minimalWireModelResult)"
default_model_display="ollama/qwen3.5:9b-4k"
fallbacks_display="ollama/qwen3.5:4b-4k, ollama/qwen3.5:2b-4k, ollama/qwen3:0.6b-4k"
if [[ "$ollama_model_tier" == "minimal_wire" ]]; then
  default_model_display="ollama/qwen3:0.6b"
  fallbacks_display="none"
fi
context_boundary_display="4096"
if [[ "$ollama_model_tier" == "minimal_wire" ]]; then
  context_boundary_display="32768"
fi

conductor_marker="/home/${USER}/openclaw_install/config/conductor_marker_v1_7.json"
if [[ -n "$CONFIG_PATH" ]]; then
  cfg_dir="$(cd "$(dirname "$CONFIG_PATH")" && pwd)"
  conductor_marker="${cfg_dir}/conductor_marker_v1_7.json"
fi
if [[ -f "$conductor_marker" ]]; then
  conductor_json="$(cat "$conductor_marker")"
else
  conductor_json="{}"
fi
host_preflight_marker="/home/${USER}/openclaw_install/config/host_preflight_marker_v1_7.json"
if [[ -n "$CONFIG_PATH" ]]; then
  cfg_dir="$(cd "$(dirname "$CONFIG_PATH")" && pwd)"
  host_preflight_marker="${cfg_dir}/host_preflight_marker_v1_7.json"
fi
if [[ -f "$host_preflight_marker" ]]; then
  host_preflight_json="$(cat "$host_preflight_marker")"
else
  host_preflight_json="{}"
fi

json_field() {
  local key="$1"
  python3 - "$conductor_json" "$key" <<'PY'
import json,sys
doc,key=sys.argv[1],sys.argv[2]
try:
    data=json.loads(doc)
except Exception:
    data={}
v=data.get(key, "UNKNOWN")
if isinstance(v, bool):
    print("true" if v else "false")
else:
    print(v if v not in [None, ""] else "UNKNOWN")
PY
}

host_field() {
  local key="$1"
  python3 - "$host_preflight_json" "$key" <<'PY'
import json,sys
doc,key=sys.argv[1],sys.argv[2]
try:
    data=json.loads(doc)
except Exception:
    data={}
v=data.get(key, "UNKNOWN")
if isinstance(v, bool):
    print("true" if v else "false")
else:
    print(v if v not in [None, ""] else "UNKNOWN")
PY
}

distro_name="$(json_field distroName)"
pkg_version="$(json_field packageVersion)"
run_supervised_wire="$(json_field runSupervisedWire)"
force_recreate="$(json_field forceRecreate)"
distro_attempted="$(json_field distroImportOrRecreateAttempted)"
distro_result="$(json_field distroImportOrRecreateResult)"
user_systemd_attempted="$(json_field userSystemdReadinessAttempted)"
user_systemd_result="$(json_field userSystemdReadinessResult)"
user_systemd_attempts="$(json_field userSystemdReadinessAttempts)"
user_systemd_substrate_probe_attempted="$(json_field userSystemdSubstrateProbeAttempted)"
user_systemd_substrate_result="$(json_field userSystemdSubstrateResult)"
user_systemd_failure_class="$(json_field userSystemdFailureClass)"
user_systemd_failure_evidence="$(json_field userSystemdFailureEvidence)"
user_systemd_recovery_attempted="$(json_field userSystemdRecoveryAttempted)"
user_systemd_linger_state="$(json_field userSystemdLingerState)"
user_systemd_runtime_dir_state="$(json_field userSystemdRuntimeDirState)"
user_systemd_bus_state="$(json_field userSystemdBusState)"
interop_append_windows_path_policy="$(json_field interopAppendWindowsPathPolicy)"
host_preflight_attempted="$(host_field hostPreflightAttempted)"
host_preflight_result="$(host_field hostPreflightResult)"
wsl_update_attempted="$(host_field wslUpdateAttempted)"
wsl_update_result="$(host_field wslUpdateResult)"
wsl_shutdown_attempted="$(host_field wslShutdownAttempted)"
wsl_shutdown_result="$(host_field wslShutdownResult)"
windows_reboot_recommended="$(host_field windowsRebootRecommended)"
resume_suggested="$(host_field resumeSuggested)"
minimal_systemd_probe_result="$(host_field minimalSystemdProbeResult)"
minimal_user_systemd_probe_result="$(host_field minimalUserSystemdProbeResult)"
if [[ "$append_windows_path_policy_marker" == "UNKNOWN" ]]; then
  append_windows_path_policy_marker="$interop_append_windows_path_policy"
fi
if [[ "$install_terminal_result" == "UNKNOWN" && "$bootstrap" == "FAIL" ]]; then
  install_terminal_result="FAIL"
fi
if [[ "$install_failure_reason" == "UNKNOWN" && "$bootstrap" == "FAIL" ]]; then
  install_failure_reason="bootstrap"
fi
if [[ "$runtime_proof_disposition" == "UNKNOWN" && "$bootstrap" == "FAIL" ]]; then
  runtime_proof_disposition="SKIPPED_INSTALL_FAILED"
fi

host="$(hostname)"
user="$(whoami)"
created="$(date -Iseconds)"
report="$RUN_DIR/WIRE_RATIFICATION_REPORT_v1_7.md"

classification_id="RC_UNKNOWN"
if [[ "$distro_name" =~ (RC[0-9]+) ]]; then
  classification_id="${BASH_REMATCH[1]}"
fi

discord_marker_state="${discord_channel_installed}|${discord_channel_configured}|${discord_channel_enabled}"
discord_contradiction_result="PASS"
discord_contradiction_reason="none"
discord_effective_config_result="$discord_config_result"
discord_effective_channel_config_result="$discord_channel_config_result"
discord_effective_channel_activation_result="$discord_channel_activation_result"

if [[ "$discord_marker_state" != "installed|configured|enabled" ]]; then
  case "$discord_marker_state" in
    "installed|not-configured|disabled")
      discord_contradiction_result="FAIL"
      discord_contradiction_reason="discord-markers-not-configured-disabled"
      ;;
    "installed|configured|disabled")
      discord_contradiction_result="FAIL"
      discord_contradiction_reason="discord-markers-configured-disabled"
      ;;
    "not-installed|configured|disabled")
      discord_contradiction_result="FAIL"
      discord_contradiction_reason="discord-markers-not-installed"
      ;;
    "not-installed|not-configured|disabled")
      discord_contradiction_result="FAIL"
      discord_contradiction_reason="discord-markers-not-installed-not-configured"
      ;;
  esac
fi

if [[ "$discord_contradiction_result" == "FAIL" ]] && \
   [[ "$discord_config_result" == "PASS" || "$discord_channel_config_result" == "PASS" || "$discord_channel_activation_result" == "PASS" ]]; then
  discord_effective_config_result="FAIL"
  discord_effective_channel_config_result="FAIL"
  discord_effective_channel_activation_result="FAIL"
fi

if [[ "$discord_plugin_installed" == "UNKNOWN" ]]; then
  case "$discord_channel_installed" in
    installed) discord_plugin_installed="YES" ;;
    not-installed) discord_plugin_installed="NO" ;;
  esac
fi
if [[ "$discord_env_token_present" == "UNKNOWN" ]]; then
  if [[ "$discord_script_env_token_present" == "YES" || "$discord_systemd_env_token_present" == "YES" || "$discord_gateway_env_token_present" == "YES" ]]; then
    discord_env_token_present="YES"
  elif [[ "$discord_script_env_token_present" == "NO" && "$discord_systemd_env_token_present" == "NO" && "$discord_gateway_env_token_present" == "NO" ]]; then
    discord_env_token_present="NO"
  fi
fi
if [[ "$discord_adapter_env_configured_plausible" == "UNKNOWN" ]]; then
  if [[ "$discord_loaded_adapter_proof_result" == "PASS" && "$discord_loaded_adapter_configured_env_only" == "YES" && "$discord_loaded_adapter_token_source_env_only" == "env" && "$discord_loaded_adapter_token_status_env_only" == "available" ]]; then
    discord_adapter_env_configured_plausible="YES"
  elif [[ "$discord_loaded_adapter_proof_attempted" == "YES" ]]; then
    discord_adapter_env_configured_plausible="NO"
  fi
fi
if [[ "$discord_public_account_recognized" == "UNKNOWN" ]]; then
  discord_account_count="$discord_public_status_accounts_count"
  [[ "$discord_account_count" =~ ^[0-9]+$ ]] || discord_account_count="$discord_accounts_json_count"
  if [[ "$discord_account_count" =~ ^[0-9]+$ && "$discord_account_count" -gt 0 ]]; then
    discord_public_account_recognized="YES"
  elif [[ "$discord_account_count" == "0" ]]; then
    discord_public_account_recognized="NO"
  fi
fi
if [[ "$discord_public_status_configured_enabled" == "UNKNOWN" ]]; then
  if [[ "$discord_marker_state" == "installed|configured|enabled" ]]; then
    discord_public_status_configured_enabled="YES"
  elif [[ "$discord_marker_state" != "unknown|unknown|unknown" ]]; then
    discord_public_status_configured_enabled="NO"
  fi
fi
if [[ "$discord_provider_startup_observed" == "UNKNOWN" ]]; then
  case "$discord_gateway_provider_startup_seen" in
    YES) discord_provider_startup_observed="YES" ;;
    NO) discord_provider_startup_observed="NO" ;;
  esac
fi
if [[ "$discord_message_proof_completed" == "UNKNOWN" ]]; then
  if [[ "$discord_manual_message_proof" == "PASS" ]]; then
    discord_message_proof_completed="YES"
  else
    discord_message_proof_completed="NOT_RUN"
  fi
fi
if [[ "$discord_verifier_allowed" == "UNKNOWN" ]]; then
  if [[ "$discord_marker_state" == "installed|configured|enabled" && "$discord_manual_message_proof" == "PASS" && "$post_install_runtime_readiness" == "PASS" ]]; then
    discord_verifier_allowed="YES"
  else
    discord_verifier_allowed="NO"
  fi
fi
if [[ "$discord_public_account_recognition_source" == "UNKNOWN" ]]; then
  discord_public_account_recognition_source="openclaw-public-channels-list-json-plugin.config.listAccountIds(cfg)"
fi

{
  echo "# OpenClaw WSL/OpenClaw Wire Ratification Report v1.7"
  echo
  echo "## Identity"
  echo "- Created: ${created}"
  echo "- Distro: ${distro_name}"
  echo "- User: ${user}"
  echo "- Host: ${host}"
  echo "- Package version: ${pkg_version}"
  echo "- Evidence root: ${RUN_DIR}"
  echo "- Supervised wire mode: ${run_supervised_wire}"
  echo "- User-systemd readiness attempted: ${user_systemd_attempted}"
  echo "- User-systemd readiness result: ${user_systemd_result}"
  echo "- User-systemd readiness attempts: ${user_systemd_attempts}"
  echo "- User-systemd substrate probe attempted: ${user_systemd_substrate_probe_attempted}"
  echo "- User-systemd substrate result: ${user_systemd_substrate_result}"
  echo "- User-systemd failure class: ${user_systemd_failure_class}"
  echo "- Host preflight attempted: ${host_preflight_attempted}"
  echo "- Host preflight result: ${host_preflight_result}"
  echo
  echo "## Result"
  echo "- WSL distro import/recreate attempted: ${distro_attempted}"
  echo "- WSL distro import/recreate: ${distro_result}"
  echo "- User-systemd readiness: ${user_systemd_result}"
  echo "- Install terminal result: ${install_terminal_result}"
  echo "- Install failure reason: ${install_failure_reason}"
  echo "- Runtime proof disposition: ${runtime_proof_disposition}"
  echo "- Baseline bootstrap: ${bootstrap}"
  echo "- Safe model aliases: ${bootstrap}"
  echo "- Direct Ollama GPU/context: ${baseline}"
  echo "- OpenClaw bounded provider surface: ${baseline}"
  echo "- Dashboard/OpenClaw inference: ${dash}"
  echo "- Discord configuration: ${dcfg}"
  echo "- Discord pairing/manual message: ${dver}"
  echo "- Optional 30B reasoning/coder tier: ${optional}"
  echo "- Roc identity/personality layer: NOT_STARTED"
  echo
  echo "## Host WSL Preflight"
  echo "- Host preflight attempted: ${host_preflight_attempted}"
  echo "- Host preflight result: ${host_preflight_result}"
  echo "- WSL update attempted: ${wsl_update_attempted}"
  echo "- WSL update result: ${wsl_update_result}"
  echo "- WSL shutdown attempted: ${wsl_shutdown_attempted}"
  echo "- WSL shutdown result: ${wsl_shutdown_result}"
  echo "- Windows reboot recommended: ${windows_reboot_recommended}"
  echo "- Resume suggested: ${resume_suggested}"
  echo "- Minimal systemd probe result: ${minimal_systemd_probe_result}"
  echo "- Minimal user-systemd probe result: ${minimal_user_systemd_probe_result}"
  echo "- Target-distro substrate probe attempted: ${user_systemd_substrate_probe_attempted}"
  echo "- Target-distro substrate result: ${user_systemd_substrate_result}"
  echo "- Target-distro failure class: ${user_systemd_failure_class}"
  echo "- Target-distro failure evidence: ${user_systemd_failure_evidence}"
  echo "- Target-distro recovery attempted: ${user_systemd_recovery_attempted}"
  echo "- Target-distro linger state: ${user_systemd_linger_state}"
  echo "- Target-distro runtime dir state: ${user_systemd_runtime_dir_state}"
  echo "- Target-distro bus state: ${user_systemd_bus_state}"
  echo "- appendWindowsPath policy: ${interop_append_windows_path_policy}"
  echo
  echo "## Stable Baseline"
  echo "- Default model: ${default_model_display}"
  echo "- Fallbacks: ${fallbacks_display}"
  echo "- Context boundary: ${context_boundary_display}"
  echo "- Gateway bind: loopback"
  echo "- Local auth: yes"
  echo "- OLLAMA_API_KEY: present/redacted"
  echo "- Discord token: present/redacted or skipped"
  echo
  echo "## Completion Proof Summary"
  echo "- Dashboard proof: ${dash}"
  echo "- Discord config: ${dcfg}"
  echo "- Discord transport: ${discord_transport_proof}"
  echo "- Discord manual message proof: ${discord_manual_message_proof}"
  echo "- Post-install runtime readiness: ${post_install_runtime_readiness}"
  echo
  echo "## Optional Operator Environment"
  echo "- Shell customization attempted: ${shell_customization_attempted}"
  echo "- Shell customization result: ${shell_customization_result}"
  echo "- Shell customization failure reason: ${shell_customization_failure_reason}"
  echo
  echo "## OpenClaw Install"
  echo "- OpenClaw npm install attempted: ${openclaw_npm_install_attempted}"
  echo "- OpenClaw npm install result: ${openclaw_npm_install_result}"
  echo "- OpenClaw npm install attempts: ${openclaw_npm_install_attempts}"
  echo "- OpenClaw npm install failure reason: ${openclaw_npm_install_failure_reason}"
  echo "- OpenClaw npm install duration seconds: ${openclaw_npm_install_duration_seconds}"
  echo "- Linux path hardening result: ${linux_path_hardening_result}"
  echo "- Linux path windows segments present: ${linux_path_windows_segments_present}"
  echo "- Linux path hardening phase: ${linux_path_hardening_phase}"
  echo "- appendWindowsPath policy marker: ${append_windows_path_policy_marker}"
  echo "- Node initial resolution: ${linux_node_resolution_initial}"
  echo "- npm initial resolution: ${linux_npm_resolution_initial}"
  echo "- OpenClaw initial resolution: ${openclaw_resolution_initial}"
  echo "- Node before Node install: ${linux_node_resolution_before_node_install}"
  echo "- npm before Node install: ${linux_npm_resolution_before_node_install}"
  echo "- OpenClaw before Node install: ${openclaw_resolution_before_node_install}"
  echo "- Node after Node install: ${linux_node_resolution_after_node_install}"
  echo "- npm after Node install: ${linux_npm_resolution_after_node_install}"
  echo "- Linux node/npm gate result: ${linux_node_npm_gate_result}"
  echo "- Node before OpenClaw install: ${linux_node_resolution_before_openclaw_install}"
  echo "- npm before OpenClaw install: ${linux_npm_resolution_before_openclaw_install}"
  echo "- OpenClaw before OpenClaw install: ${openclaw_resolution_before_openclaw_install}"
  echo "- OpenClaw after OpenClaw install: ${openclaw_resolution_after_openclaw_install}"
  echo "- OpenClaw command resolution guard result: ${openclaw_command_resolution_guard_result}"
  echo
  echo "## OpenClaw Reproducibility"
  echo "- Expected package spec: ${openclaw_expected_package_spec}"
  echo "- Expected observed identity: ${openclaw_expected_identity}"
  echo "- Observed identity: ${openclaw_observed_identity}"
  echo "- Identity verification result: ${openclaw_identity_verification_result}"
  echo "- Identity verification reason: ${openclaw_identity_verification_reason}"
  echo "- Observed package name: ${openclaw_identity_observed_package_name}"
  echo "- Observed package version: ${openclaw_identity_observed_package_version}"
  echo "- Observed gitHead: ${openclaw_identity_observed_git_head}"
  echo "- Compatibility privilege mode: ${openclaw_compatibility_privilege_mode}"
  echo "- Compatibility privilege result: ${openclaw_compatibility_privilege_result}"
  echo "- Compatibility privilege reason: ${openclaw_compatibility_privilege_reason}"
  echo "- v92 compatibility result: ${openclaw_compatibility_v92_result}"
  echo "- v92 compatibility reason: ${openclaw_compatibility_v92_reason}"
  echo "- v92 target path: ${openclaw_compatibility_v92_target_path}"
  echo "- v92 pre hash: ${openclaw_compatibility_v92_pre_hash}"
  echo "- v92 post hash: ${openclaw_compatibility_v92_post_hash}"
  echo "- v92 anchor counts: ${openclaw_compatibility_v92_anchor_counts}"
  echo "- v92 current structure counts: ${openclaw_compatibility_v92_current_structure_counts}"
  echo "- v92 selected strategy: ${openclaw_compatibility_v92_selected_strategy}"
  echo "- v92 accepted final hashes: ${openclaw_compatibility_v92_accepted_final_hashes}"
  echo "- v99 compatibility result: ${openclaw_compatibility_v99_result}"
  echo "- Consolidated v102/v103 compatibility result: ${openclaw_compatibility_v103_result}"
  echo "- Compatibility stage result: ${openclaw_compatibility_stage_result}"
  echo "- Compatibility stage reason: ${openclaw_compatibility_stage_reason}"
  echo "- Static validation result: ${openclaw_compatibility_validation_result}"
  echo "- Static validation reason: ${openclaw_compatibility_validation_reason}"
  echo "- Compatibility stage report: ${openclaw_compatibility_stage_report_path}"
  echo
  echo "## Ollama Model Tier"
  echo "- Ollama model tier: ${ollama_model_tier}"
  echo "- Ollama model pull attempted: ${ollama_model_pull_attempted}"
  echo "- Ollama model pull result: ${ollama_model_pull_result}"
  echo "- Ollama model pull failure reason: ${ollama_model_pull_failure_reason}"
  echo "- Ollama model pull attempts: ${ollama_model_pull_attempts}"
  echo "- Preferred safe model tier result: ${preferred_safe_model_tier_result}"
  echo "- Minimal wire model result: ${minimal_wire_model_result}"
  echo
  echo "## Human Gates Exercised"
  echo "- ForceRecreate approved: ${force_recreate}"
  echo "- Dashboard auth URL copied: ${dashboard_auth_url_copied}"
  echo "- Dashboard open requested: ${dashboard_open_requested}"
  echo "- Dashboard auto-open result: ${dashboard_auto_open_result}"
  echo "- Dashboard prompt surfaced: ${dashboard_prompt_surfaced}"
  echo "- Discord token provided: ${discord_token_provided}"
  echo "- Discord token prompt surfaced: ${discord_token_prompt_surfaced}"
  echo "- Discord token source: ${discord_token_source}"
  echo "- Discord token file configured: ${discord_token_file_configured}"
  echo "- Discord token file present: ${discord_token_file_present}"
  echo "- Discord token file non-empty: ${discord_token_file_non_empty}"
  echo "- Discord token read result: ${discord_token_read_result}"
  echo "- Discord token value logged: ${discord_token_value_logged}"
  echo "- Discord runtime secret handling: ${discord_runtime_secret_handling}"
  echo "- Discord runtime secret persistence: ${discord_runtime_secret_persistence}"
  echo "- Discord token durable exposure: ${discord_token_durable_exposure}"
  echo "- Discord token install_config value stored: ${discord_token_install_config_value_stored}"
  echo "- Discord refresh-token requested: ${discord_refresh_token_requested}"
  echo "- Dashboard prompt manually sent: ${dashboard_prompt_sent}"
  echo "- Discord pairing prompt surfaced: ${discord_pairing_prompt_surfaced}"
  echo "- Discord manual proof prompt surfaced: ${discord_manual_proof_prompt_surfaced}"
  echo "- Discord pairing approved: ${discord_pairing_approved}"
  echo "- Discord prompt manually sent: ${discord_prompt_sent}"
  echo
  echo "## Discord Configuration"
  echo "- Discord config model tier: ${discord_config_model_tier}"
  echo "- Discord config expected primary model: ${discord_config_expected_primary_model}"
  echo "- Discord config model guard result: ${discord_config_model_guard_result}"
  echo "- Discord config failure reason: ${discord_config_failure_reason}"
  echo "- OpenClaw read-only external plugins patch result: ${openclaw_readonly_external_plugins_patch_result}"
  echo "- OpenClaw read-only external plugins patch proof: ${openclaw_readonly_external_plugins_patch_proof}"
  echo "- Discord native channel add attempted: ${discord_native_channel_add_attempted}"
  echo "- Discord native channel add methods tried: ${discord_native_channel_add_methods_tried}"
  echo "- Discord native channel add final method: ${discord_native_channel_add_final_method}"
  echo "- Discord native channel add command result: ${discord_native_channel_add_command_result}"
  echo "- Discord native channel add state result: ${discord_native_channel_add_state_result}"
  echo "- Discord native channel add result: ${discord_native_channel_add_result}"
  echo "- Discord native channel add failure reason: ${discord_native_channel_add_failure_reason}"
  echo "- Discord setup method: ${discord_setup_method}"
  echo "- Discord SecretRef config attempted: ${discord_secretref_config_attempted}"
  echo "- Discord SecretRef config result: ${discord_secretref_config_result}"
  echo "- Discord SecretRef config failure reason: ${discord_secretref_config_failure_reason}"
  echo "- Discord enabled config result: ${discord_enabled_config_result}"
  echo "- Discord account-scoped config attempted: ${discord_account_scoped_config_attempted}"
  echo "- Discord account-scoped config result: ${discord_account_scoped_config_result}"
  echo "- Discord account-scoped config failure reason: ${discord_account_scoped_config_failure_reason}"
  echo "- Discord account-scoped token result: ${discord_account_scoped_token_result}"
  echo "- Discord account-scoped enabled result: ${discord_account_scoped_enabled_result}"
  echo "- Discord env-only implicit default attempted: ${discord_env_only_implicit_default_attempted}"
  echo "- Discord env-only implicit default result: ${discord_env_only_implicit_default_result}"
  echo "- Discord env-only implicit default failure reason: ${discord_env_only_implicit_default_failure_reason}"
  echo "- Discord plugin-entry gate attempted: ${discord_plugin_entry_gate_attempted}"
  echo "- Discord plugin-entry gate result: ${discord_plugin_entry_gate_result}"
  echo "- Discord plugin-entry gate failure reason: ${discord_plugin_entry_gate_failure_reason}"
  echo "- Discord plugin-entry keys: ${discord_plugin_entry_keys}"
  echo "- Discord plugin-entry Discord present: ${discord_plugin_entry_discord_present}"
  echo "- Discord plugin-entry Discord enabled: ${discord_plugin_entry_discord_enabled}"
  echo "- Discord plugin-entry config validate result: ${discord_plugin_entry_config_validate_result}"
  echo "- Discord deep status gate result: ${discord_deep_status_gate_result}"
  echo "- Discord deep status gate failure reason: ${discord_deep_status_gate_failure_reason}"
  echo "- Discord deep status has Discord: ${discord_deep_status_has_discord}"
  echo "- Discord deep status no channels configured: ${discord_deep_status_no_channels_configured}"
  echo "- Discord top-level token removed for env-only: ${discord_top_level_token_removed_for_env_only}"
  echo "- Discord account-scoped token removed for env-only: ${discord_account_scoped_token_removed_for_env_only}"
  echo "- Discord script env token present: ${discord_script_env_token_present}"
  echo "- Discord script env token length: ${discord_script_env_token_length}"
  echo "- Discord systemd env token present: ${discord_systemd_env_token_present}"
  echo "- Discord systemd env token length: ${discord_systemd_env_token_length}"
  echo "- Discord gateway env token present: ${discord_gateway_env_token_present}"
  echo "- Discord gateway env token length: ${discord_gateway_env_token_length}"
  echo "- Discord CLI env injected for status: ${discord_cli_env_injected_for_status}"
  echo "- Discord CLI env injected accounts JSON count: ${discord_cli_env_injected_accounts_json_count}"
  echo "- Discord CLI env injected line: ${discord_cli_env_injected_line}"
  echo "- Discord inactive surface warning seen: ${discord_inactive_surface_warning_seen}"
  echo "- Discord accounts JSON count: ${discord_accounts_json_count}"
  echo "- Discord loaded adapter proof attempted: ${discord_loaded_adapter_proof_attempted}"
  echo "- Discord loaded adapter proof result: ${discord_loaded_adapter_proof_result}"
  echo "- Discord loaded adapter proof failure reason: ${discord_loaded_adapter_proof_failure_reason}"
  echo "- Discord loaded adapter ids env-only: ${discord_loaded_adapter_ids_env_only}"
  echo "- Discord loaded adapter default account id env-only: ${discord_loaded_adapter_default_account_id_env_only}"
  echo "- Discord loaded adapter configured env-only: ${discord_loaded_adapter_configured_env_only}"
  echo "- Discord loaded adapter token source env-only: ${discord_loaded_adapter_token_source_env_only}"
  echo "- Discord loaded adapter token status env-only: ${discord_loaded_adapter_token_status_env_only}"
  echo "- Discord loaded adapter token length env-only: ${discord_loaded_adapter_token_length_env_only}"
  echo "- Discord loaded adapter ids explicit default: ${discord_loaded_adapter_ids_explicit_default}"
  echo "- Discord loaded adapter configured explicit default: ${discord_loaded_adapter_configured_explicit_default}"
  echo "- Discord public status accounts count: ${discord_public_status_accounts_count}"
  echo "- Discord status-layer lazy plugin bug suspected: ${discord_status_layer_lazy_plugin_bug_suspected}"
  echo "- Discord failure class: ${discord_failure_class}"
  echo "- Discord rollback decision: ${discord_rollback_decision}"
  echo "- Discord rollback reason: ${discord_rollback_reason}"
  echo "- Discord env-only config preserved: ${discord_env_only_config_preserved}"
  echo "- Discord known-bad SecretRef restore skipped: ${discord_known_bad_secretref_restore_skipped}"
  echo "- Discord post-failure config has top-level token: ${discord_post_failure_config_has_top_level_token}"
  echo "- Discord post-failure config shape: ${discord_post_failure_config_shape}"
  echo "- Discord gateway provider startup seen: ${discord_gateway_provider_startup_seen}"
  echo "- Discord gateway provider startup pattern: ${discord_gateway_provider_startup_pattern}"
  echo "- Discord gateway generic ready only: ${discord_gateway_generic_ready_only}"
  echo "- Discord gateway provider startup detection result: ${discord_gateway_provider_startup_detection_result}"
  echo "- Discord gateway provider startup matched line: ${discord_gateway_provider_startup_matched_line}"
  echo "- Discord gateway provider startup matched line SHA-256: ${discord_gateway_provider_startup_matched_line_sha256}"
  echo "- Discord runtime may still work: ${discord_runtime_may_still_work}"
  echo
  echo "## Discord State Taxonomy"
  echo "- Discord plugin installed: ${discord_plugin_installed}"
  echo "- Discord env token present: ${discord_env_token_present}"
  echo "- Discord adapter env configured plausible: ${discord_adapter_env_configured_plausible}"
  echo "- Discord public account recognized: ${discord_public_account_recognized}"
  echo "- Discord public account recognition source: ${discord_public_account_recognition_source}"
  echo "- Discord public status configured/enabled: ${discord_public_status_configured_enabled}"
  echo "- Discord provider startup observed: ${discord_provider_startup_observed}"
  echo "- Discord message proof completed: ${discord_message_proof_completed}"
  echo "- Discord transport proof: ${discord_transport_proof}"
  echo "- Discord manual message proof: ${discord_manual_message_proof}"
  echo "- Discord verifier allowed: ${discord_verifier_allowed}"
  echo "- Discord taxonomy note: plugin installed plus env token present does not imply public account recognition, provider startup, or message proof."
  if [[ "$discord_loaded_adapter_proof_result" == "PASS" && "$discord_marker_state" != "installed|configured|enabled" ]]; then
    echo "- Discord adapter/public status classification: Adapter proof: PASS; Public Discord status: FAIL; Overall Discord config: FAIL; Rollback decision: ${discord_rollback_decision}"
  fi
  echo "- Discord line before native add: ${discord_line_before_native_add}"
  echo "- Discord line after use-env: ${discord_line_after_use_env}"
  echo "- Discord line after token-file: ${discord_line_after_token_file}"
  echo "- Discord line after bot-token: ${discord_line_after_bot_token}"
  echo "- Discord line after native add: ${discord_line_after_native_add}"
  echo "- Discord line after SecretRef config: ${discord_line_after_secretref_config}"
  echo "- Discord line after account-scoped config: ${discord_line_after_account_scoped_config}"
  echo "- Discord line after env-only implicit default: ${discord_line_after_env_only_implicit_default}"
  echo "- Discord channel state parser result: ${discord_channel_state_parser_result}"
  echo "- Discord channel state before repair: ${discord_channel_state_before_repair}"
  echo "- Discord repair attempted: ${discord_repair_attempted}"
  echo "- Discord repair method: ${discord_repair_method}"
  echo "- Discord repair result: ${discord_repair_result}"
  echo "- Discord repair failure reason: ${discord_repair_failure_reason}"
  echo "- Discord channel state after repair: ${discord_channel_state_after_repair}"
  echo "- Discord channel installed: ${discord_channel_installed}"
  echo "- Discord channel configured: ${discord_channel_configured}"
  echo "- Discord channel enabled: ${discord_channel_enabled}"
  echo "- Discord marker state: ${discord_marker_state}"
  echo "- Discord external plugin install required: ${discord_external_plugin_install_required}"
  echo "- Discord external plugin install attempted: ${discord_external_plugin_install_attempted}"
  echo "- Discord external plugin install result: ${discord_external_plugin_install_result}"
  echo "- Discord channel config result: ${discord_effective_channel_config_result}"
  echo "- Discord channel activation result: ${discord_effective_channel_activation_result}"
  echo "- Discord config result: ${discord_effective_config_result}"
  echo "- Discord contradiction check: ${discord_contradiction_result}"
  echo "- Discord contradiction reason: ${discord_contradiction_reason}"
  echo
  echo "## Dashboard Proof"
  echo "- Dashboard transport proof: ${dashboard_transport_proof}"
  echo "- Dashboard model loaded proof: ${dashboard_model_loaded_proof}"
  echo "- Dashboard GPU/context proof: ${dashboard_gpu_context_proof}"
  echo "- Dashboard exact-response proof: ${dashboard_exact_response_proof}"
  echo "- Dashboard verifier result: ${dashboard_verifier_result}"
  echo "- Dashboard failure reason: ${dashboard_failure_reason}"
  echo "- Dashboard auth helper result: ${dashboard_auth_helper_result}"
  echo "- Dashboard material failure lines count: ${dashboard_material_failure_lines_count}"
  echo "- Dashboard compaction diagnostic noise: ${dashboard_compaction_diagnostic_noise}"
  echo "- Dashboard compaction diagnostic lines count: ${dashboard_compaction_diagnostic_lines_count}"
  echo "- Dashboard auth probe noise: ${dashboard_auth_probe_noise}"
  echo "- Dashboard auth probe noise lines count: ${dashboard_auth_probe_noise_lines_count}"
  echo "- Dashboard device-token probe noise: ${dashboard_device_probe_noise}"
  echo "- Dashboard device-token probe noise lines count: ${dashboard_device_probe_noise_lines_count}"
  echo
  echo "## Final Runtime Readiness"
  echo "- Post-install runtime readiness: ${post_install_runtime_readiness}"
  echo "- Final gateway status: ${final_gateway_status}"
  echo "- Final Discord status: ${final_discord_status}"
  echo
  echo "## Evidence Archives"
  echo "- bootstrap archive: ${RUN_DIR}/bootstrap.log"
  echo "- baseline verification archive: ${RUN_DIR}/baseline_verifier.log"
  echo "- dashboard verification archive: ${RUN_DIR}/dashboard_verifier.log"
  echo "- Discord configuration archive: ${RUN_DIR}/discord_config.log"
  echo "- Discord verification archive: ${RUN_DIR}/discord_verifier.log"
  echo "- final wire archive: ${RUN_DIR}"
  echo
  echo "## Classification"
  echo "- ${classification_id} safe baseline install: ${bootstrap}"
  echo "- ${classification_id} dashboard verification: ${dash}"
  echo "- ${classification_id} Discord verification: ${dver}"
  echo "- ${classification_id} post-install runtime readiness: ${runtime_ready}"
  echo "- ${classification_id} optional 30B reasoning/coder tier: ${optional}"
  echo "- Roc identity/personality layer: NOT_STARTED"
} > "$report"

echo "$report"
