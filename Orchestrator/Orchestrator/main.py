import json
import sys
from datetime import datetime, timezone

from orchestrator.engine import process_next_task, process_task_by_id
from orchestrator.intake import (
    assess_decomposition_handoff_admission,
    authorize_case_packet_creation_from_seed_review,
    judge_intake,
    review_case_packet_seed_candidate,
)
from orchestrator.case_packet import (
    append_case_packet_entry,
    get_case_packet_orientation_fields,
    initialize_case_packet_from_seed,
    summarize_case_packet,
    load_case_packet,
    normalize_case_packet,
    save_case_packet,
    update_case_packet_orientation,
    validate_case_packet,
)
from orchestrator.paths import (
    ARTIFACTS_DIR,
    DATA_DIR,
    DOCS_DIR,
    LOGS_DIR,
    PROJECT_ROOT,
    RUNS_DIR,
    STATE_DIR,
    TASKS_DIR,
    resolve_project_path,
)
from orchestrator.run_manager import (
    create_repair_task_from_failed_result,
    create_followup_review_task_from_needs_review_result,
    create_run,
    find_live_response_task_duplicate,
    get_task_recommendation_reason,
    get_task_recommendation_type,
    is_post_execution_recommendation_result_task,
    is_ready_execution_candidate_task,
    is_ready_recommendation_created_task,
    is_recommendation_created_task,
    load_confirmed_recommendation_created_tasks_for_run,
    load_post_execution_recommendation_result_tasks_for_run,
    load_ready_execution_candidate_tasks_for_run,
    load_ready_recommendation_created_tasks_for_run,
    load_recommendation_created_tasks_for_run,
    load_task,
    save_task,
)
from orchestrator.recommendation_store import load_recommendation_records_for_run
from orchestrator.recommendation_cli import (
    accept_recommendation as cli_accept_recommendation,
    archive_recommendation as cli_archive_recommendation,
    print_recommendation_actions as cli_print_recommendation_actions,
    print_recommendation_drafts as cli_print_recommendation_drafts,
    print_recommendation_outcomes as cli_print_recommendation_outcomes,
    print_recommendation_resolution as cli_print_recommendation_resolution,
    print_recommendation_summary as cli_print_recommendation_summary,
    print_recommendations as cli_print_recommendations,
)
from orchestrator.case_packet_persistence import persist_case_packet_from_creation_authorization
from orchestrator.case_packet_task_candidate_review import review_persisted_case_packet_task_candidate
from orchestrator.case_packet_task_creation_authorization import authorize_task_creation_from_case_packet_candidate_review
from orchestrator.case_packet_task_creation_write_gate import create_task_from_authorized_case_packet_task_creation
from orchestrator.case_packet_task_execution_candidate_surface import surface_case_packet_task_execution_candidates
from orchestrator.case_packet_task_execution_authorization import authorize_case_packet_task_execution_from_candidate_surface
from orchestrator.authorized_case_packet_task_execution import execute_authorized_case_packet_task
from orchestrator.case_packet_task_execution_result_review import review_case_packet_task_execution_result
from orchestrator.case_packet_task_execution_result_response_options import surface_case_packet_task_execution_result_response_options
from orchestrator.current_success_result_review import review_current_success_task_result
from orchestrator.current_success_acceptance import record_current_success_result_acceptance
from orchestrator.state import load_state, save_state
from verifiers.registry import run_check

REQUIRED_DIRS = [
    PROJECT_ROOT / "orchestrator",
    PROJECT_ROOT / "providers",
    PROJECT_ROOT / "verifiers",
    PROJECT_ROOT / "agents",
    DOCS_DIR,
    DATA_DIR,
    STATE_DIR,
    RUNS_DIR,
    TASKS_DIR,
    ARTIFACTS_DIR,
    LOGS_DIR,
]


def initialize_workspace() -> None:
    for directory in REQUIRED_DIRS:
        directory.mkdir(parents=True, exist_ok=True)

    state = load_state()
    state["workspace_initialized"] = True
    save_state(state)

    print("Workspace initialized successfully.")


def _load_recommendation_created_tasks_for_run(run_id: str) -> list:
    return load_recommendation_created_tasks_for_run(run_id)


def _load_ready_recommendation_tasks_for_run(run_id: str) -> list:
    return load_ready_recommendation_created_tasks_for_run(run_id)


def _load_ready_execution_candidates_for_run(run_id: str) -> list:
    return load_ready_execution_candidate_tasks_for_run(run_id)


def print_status() -> None:
    print("System is operational.")
    state = load_state()
    run_id = state.get("active_run_id")
    if not run_id:
        return

    records = load_recommendation_records_for_run(str(run_id))
    print(f"Active run: {run_id}")
    print(f"Recommendation records for active run: {len(records)}")
    print(f"Recommendation records exist: {'yes' if records else 'no'}")
    recommendation_created_tasks = _load_recommendation_created_tasks_for_run(str(run_id))
    ready_tasks = _load_ready_recommendation_tasks_for_run(str(run_id))
    confirmed_count = len(ready_tasks)
    total_count = len(recommendation_created_tasks)
    print(f"Recommendation-created tasks: {total_count}")
    print(f"Confirmed recommendation-created tasks: {confirmed_count}")
    print(f"Unconfirmed recommendation-created tasks: {total_count - confirmed_count}")
    print(f"Ready recommendation-created tasks: {len(ready_tasks)}")


def create_new_run() -> None:
    request_text = " ".join(sys.argv[2:]).strip() or "Stub request"
    run = create_run(request_text)
    print(f"Run created: {run['id']}")


def _read_json_object_input(input_path_text: str, usage_label: str) -> dict | None:
    input_path = resolve_project_path(input_path_text)
    if not input_path.exists() or not input_path.is_file():
        print(f"{usage_label} input file not found: {input_path}")
        return None

    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(f"Invalid JSON input file: {error}")
        return None
    except OSError as error:
        print(f"Unable to read {usage_label.lower()} input file: {error}")
        return None

    if not isinstance(payload, dict):
        print(f"{usage_label} input JSON must be an object.")
        return None

    return payload


def run_intake_judge() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py intake-judge <intake_input_json_path>")
        return

    payload = _read_json_object_input(sys.argv[2], "Intake")
    if payload is None:
        return

    result = judge_intake(payload)
    print(json.dumps(result, indent=2))


def run_intake_handoff_admit() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py intake-handoff-admit <intake_result_or_handoff_json_path>")
        return

    payload = _read_json_object_input(sys.argv[2], "Intake handoff admission")
    if payload is None:
        return

    result = assess_decomposition_handoff_admission(payload)
    print(json.dumps(result, indent=2))



def run_case_packet_seed_review() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py case-packet-seed-review <intake_result_or_handoff_json_path>")
        return

    payload = _read_json_object_input(sys.argv[2], "Case-packet seed review")
    if payload is None:
        return

    result = review_case_packet_seed_candidate(payload)
    print(json.dumps(result, indent=2))


def run_case_packet_creation_authorize() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py case-packet-creation-authorize <seed_review_or_authorization_json_path>")
        return

    payload = _read_json_object_input(sys.argv[2], "Case-packet creation authorization")
    if payload is None:
        return

    result = authorize_case_packet_creation_from_seed_review(payload)
    print(json.dumps(result, indent=2))



def run_case_packet_persist_authorized() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py case-packet-persist-authorized <phase67_authorization_or_persistence_json_path>")
        return

    payload = _read_json_object_input(sys.argv[2], "Case-packet authorized persistence")
    if payload is None:
        return

    result = persist_case_packet_from_creation_authorization(payload)
    print(json.dumps(result, indent=2))


def run_case_packet_task_candidate_review() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py case-packet-task-candidate-review <case_packet_review_input_json_path>")
        return

    payload = _read_json_object_input(sys.argv[2], "Case-packet task candidate review")
    if payload is None:
        return

    result = review_persisted_case_packet_task_candidate(payload)
    print(json.dumps(result, indent=2))



def run_case_packet_task_creation_authorize() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py case-packet-task-creation-authorize <phase69_review_or_authorization_json_path>")
        return

    payload = _read_json_object_input(sys.argv[2], "Case-packet task creation authorization")
    if payload is None:
        return

    result = authorize_task_creation_from_case_packet_candidate_review(payload)
    print(json.dumps(result, indent=2))


def run_case_packet_task_create_authorized() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py case-packet-task-create-authorized <phase70_authorization_json_path>")
        return

    payload = _read_json_object_input(sys.argv[2], "Case-packet authorized task creation")
    if payload is None:
        return

    result = create_task_from_authorized_case_packet_task_creation(payload)
    print(json.dumps(result, indent=2))


def run_case_packet_task_execution_authorize() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py case-packet-task-execution-authorize <phase72_candidate_surface_or_authorization_json_path>")
        return

    payload = _read_json_object_input(sys.argv[2], "Case-packet task execution authorization")
    if payload is None:
        return

    result = authorize_case_packet_task_execution_from_candidate_surface(payload)
    print(json.dumps(result, indent=2))


def run_case_packet_task_execute_authorized() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py case-packet-task-execute-authorized <phase73_authorization_json_path>")
        return

    payload = _read_json_object_input(sys.argv[2], "Authorized case-packet task execution")
    if payload is None:
        return

    result = execute_authorized_case_packet_task(payload)
    print(json.dumps(result, indent=2))


def run_case_packet_task_execution_result_review() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py case-packet-task-execution-result-review <phase74_execution_result_json_path>")
        return

    payload = _read_json_object_input(sys.argv[2], "Case-packet task execution result review")
    if payload is None:
        return

    result = review_case_packet_task_execution_result(payload)
    print(json.dumps(result, indent=2))


def run_case_packet_task_execution_result_options() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py case-packet-task-execution-result-options <phase75_review_result_json_path>")
        return

    payload = _read_json_object_input(sys.argv[2], "Case-packet task execution result response options")
    if payload is None:
        return

    result = surface_case_packet_task_execution_result_response_options(payload)
    print(json.dumps(result, indent=2))




def run_current_success_result_review() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py current-success-result-review <task_id>")
        return

    result = review_current_success_task_result({"task_id": sys.argv[2]})
    print(json.dumps(result, indent=2))



def run_current_success_result_accept() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py current-success-result-accept <acceptance_input_json_path>")
        return

    payload = _read_json_object_input(sys.argv[2], "Current success result acceptance")
    if payload is None:
        return

    result = record_current_success_result_acceptance(payload)
    print(json.dumps(result, indent=2))

def run_case_packet_create() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py case-packet-create <case_packet_input_json_path>")
        return

    input_path = resolve_project_path(sys.argv[2])
    if not input_path.exists() or not input_path.is_file():
        print(f"Case packet input file not found: {input_path}")
        return

    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(f"Invalid JSON input file: {error}")
        return
    except OSError as error:
        print(f"Unable to read case packet input file: {error}")
        return

    if not isinstance(payload, dict):
        print("Case packet input JSON must be an object.")
        return

    packet = normalize_case_packet(payload)
    validation = validate_case_packet(packet)
    if not validation.get("valid", False):
        print(json.dumps(validation, indent=2))
        return

    try:
        path = save_case_packet(packet)
    except ValueError as error:
        print(f"Invalid case packet: {error}")
        return

    print(
        json.dumps(
            {
                "created": True,
                "case_id": packet.get("case_id"),
                "path": str(path),
                "validation": validation,
            },
            indent=2,
        )
    )


def run_case_packet_show() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py case-packet-show <case_id>")
        return

    case_id = sys.argv[2]
    try:
        packet = load_case_packet(case_id)
    except ValueError as error:
        print(f"Invalid case_id: {error}")
        return
    except FileNotFoundError:
        print(f"Case packet not found: {case_id}")
        return

    print(json.dumps(packet, indent=2))


def run_case_packet_summary() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py case-packet-summary <case_id>")
        return

    case_id = sys.argv[2]
    try:
        packet = load_case_packet(case_id)
    except ValueError as error:
        print(f"Invalid case_id: {error}")
        return
    except FileNotFoundError:
        print(f"Case packet not found: {case_id}")
        return

    summary = summarize_case_packet(packet)
    print(json.dumps(summary, indent=2))


def run_case_packet_validate() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py case-packet-validate <case_id>")
        return

    case_id = sys.argv[2]
    try:
        packet = load_case_packet(case_id)
    except ValueError as error:
        print(f"Invalid case_id: {error}")
        return
    except FileNotFoundError:
        print(f"Case packet not found: {case_id}")
        return

    validation = validate_case_packet(packet)
    print(json.dumps(validation, indent=2))


def run_case_packet_init() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py case-packet-init <case_packet_seed_json_path>")
        return

    input_path = resolve_project_path(sys.argv[2])
    if not input_path.exists() or not input_path.is_file():
        print(f"Case packet seed file not found: {input_path}")
        return

    try:
        seed = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(json.dumps({"created": False, "initialized": False, "error": f"Invalid JSON input file: {error}"}, indent=2))
        return
    except OSError as error:
        print(json.dumps({"created": False, "initialized": False, "error": f"Unable to read case packet seed file: {error}"}, indent=2))
        return

    if not isinstance(seed, dict):
        print(json.dumps({"created": False, "initialized": False, "error": "Case packet seed JSON must be an object."}, indent=2))
        return

    packet = initialize_case_packet_from_seed(seed)
    validation = validate_case_packet(packet)
    if not validation.get("valid", False):
        print(
            json.dumps(
                {
                    "created": False,
                    "initialized": True,
                    "case_id": packet.get("case_id", ""),
                    "validation": validation,
                },
                indent=2,
            )
        )
        return

    try:
        path = save_case_packet(packet)
    except ValueError as error:
        print(
            json.dumps(
                {
                    "created": False,
                    "initialized": True,
                    "case_id": packet.get("case_id", ""),
                    "validation": {"valid": False, "errors": [str(error)]},
                },
                indent=2,
            )
        )
        return

    summary = summarize_case_packet(packet)
    print(
        json.dumps(
            {
                "created": True,
                "initialized": True,
                "case_id": packet.get("case_id"),
                "path": str(path),
                "validation": validation,
                "summary": summary,
                "readiness": summary.get("readiness"),
            },
            indent=2,
        )
    )


def run_case_packet_append() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py case-packet-append <case_packet_append_json_path>")
        return

    input_path = resolve_project_path(sys.argv[2])
    if not input_path.exists() or not input_path.is_file():
        print(f"Case packet append file not found: {input_path}")
        return

    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(json.dumps({"updated": False, "appended": False, "error": f"Invalid JSON input file: {error}"}, indent=2))
        return
    except OSError as error:
        print(json.dumps({"updated": False, "appended": False, "error": f"Unable to read case packet append file: {error}"}, indent=2))
        return

    if not isinstance(payload, dict):
        print(json.dumps({"updated": False, "appended": False, "error": "Case packet append JSON must be an object."}, indent=2))
        return

    case_id = str(payload.get("case_id", "")).strip()
    field = str(payload.get("field", "")).strip()
    has_entry = "entry" in payload
    entry = payload.get("entry")

    errors: list[str] = []
    if not case_id:
        errors.append("case_id is required")
    if not field:
        errors.append("field is required")
    if not has_entry:
        errors.append("entry is required")
    elif entry is None:
        errors.append("entry must not be null")

    if errors:
        print(json.dumps({"updated": False, "appended": False, "errors": errors}, indent=2))
        return

    try:
        packet = load_case_packet(case_id)
    except ValueError as error:
        print(json.dumps({"updated": False, "appended": False, "error": str(error)}, indent=2))
        return
    except FileNotFoundError:
        print(f"Case packet not found: {case_id}")
        return

    try:
        updated_packet = append_case_packet_entry(packet=packet, field=field, entry=entry)
    except ValueError as error:
        print(json.dumps({"updated": False, "appended": False, "error": str(error)}, indent=2))
        return

    validation = validate_case_packet(updated_packet)
    if not validation.get("valid", False):
        print(
            json.dumps(
                {
                    "updated": False,
                    "appended": False,
                    "case_id": case_id,
                    "field": field,
                    "validation": validation,
                },
                indent=2,
            )
        )
        return

    path = save_case_packet(updated_packet)
    print(
        json.dumps(
            {
                "updated": True,
                "appended": True,
                "case_id": case_id,
                "field": field,
                "new_count": len(updated_packet[field]),
                "path": str(path),
                "validation": validation,
            },
            indent=2,
        )
    )


def run_case_packet_orient() -> None:
    if len(sys.argv) < 3:
        print("Usage: python main.py case-packet-orient <case_packet_orientation_json_path>")
        return

    input_path = resolve_project_path(sys.argv[2])
    if not input_path.exists() or not input_path.is_file():
        print(f"Case packet orientation file not found: {input_path}")
        return

    try:
        payload = json.loads(input_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        print(json.dumps({"updated": False, "oriented": False, "error": f"Invalid JSON input file: {error}"}, indent=2))
        return
    except OSError as error:
        print(
            json.dumps(
                {"updated": False, "oriented": False, "error": f"Unable to read case packet orientation file: {error}"},
                indent=2,
            )
        )
        return

    if not isinstance(payload, dict):
        print(json.dumps({"updated": False, "oriented": False, "error": "Case packet orientation JSON must be an object."}, indent=2))
        return

    forbidden_scalar_fields = {"case_type", "title", "objective"}
    forbidden_list_fields = {
        "counterparties",
        "source_materials",
        "extracted_facts",
        "timeline_events",
        "open_issues",
        "missing_evidence",
        "contradictions",
        "drafts",
        "decisions",
    }
    orientation_fields = set(get_case_packet_orientation_fields())
    allowed_fields = {"case_id"} | orientation_fields

    errors: list[str] = []
    case_id = str(payload.get("case_id", "")).strip()
    if not case_id:
        errors.append("case_id is required")

    provided_orientation_fields = [field for field in get_case_packet_orientation_fields() if field in payload]
    if not provided_orientation_fields:
        errors.append("at least one of status or next_step is required")

    for field in payload.keys():
        if field in allowed_fields:
            continue
        if field in forbidden_scalar_fields:
            errors.append(f"field is not orientation-updatable: {field}")
        elif field in forbidden_list_fields:
            errors.append(f"field is list-based and not orientation-updatable: {field}")
        else:
            errors.append(f"unknown field: {field}")

    if errors:
        print(json.dumps({"updated": False, "oriented": False, "errors": errors}, indent=2))
        return

    updates = {field: payload[field] for field in provided_orientation_fields}

    try:
        packet = load_case_packet(case_id)
    except ValueError as error:
        print(json.dumps({"updated": False, "oriented": False, "error": str(error)}, indent=2))
        return
    except FileNotFoundError:
        print(f"Case packet not found: {case_id}")
        return

    try:
        updated_packet = update_case_packet_orientation(packet=packet, updates=updates)
    except ValueError as error:
        print(json.dumps({"updated": False, "oriented": False, "error": str(error)}, indent=2))
        return

    validation = validate_case_packet(updated_packet)
    if not validation.get("valid", False):
        print(
            json.dumps(
                {
                    "updated": False,
                    "oriented": False,
                    "case_id": case_id,
                    "updated_fields": provided_orientation_fields,
                    "validation": validation,
                },
                indent=2,
            )
        )
        return

    path = save_case_packet(updated_packet)
    print(
        json.dumps(
            {
                "updated": True,
                "oriented": True,
                "case_id": case_id,
                "updated_fields": provided_orientation_fields,
                "path": str(path),
                "validation": validation,
            },
            indent=2,
        )
    )


def _parse_provider_for_next() -> str:
    provider = "mock"
    args = sys.argv[2:]

    if "--provider" in args:
        index = args.index("--provider")
        if index + 1 >= len(args):
            print("Usage: python main.py next [--provider <provider_name>]")
            return ""
        provider = args[index + 1].strip()
        if not provider:
            print("Usage: python main.py next [--provider <provider_name>]")
            return ""

    return provider


def _parse_run_filter_for_recommendations() -> str | None:
    args = sys.argv[2:]
    if "--run" not in args:
        return None

    index = args.index("--run")
    if index + 1 >= len(args):
        print("Usage: python main.py recommendations [--run <run_id>]")
        return ""
    run_id = args[index + 1].strip()
    if not run_id:
        print("Usage: python main.py recommendations [--run <run_id>]")
        return ""
    return run_id


def _parse_run_filter_for_recommendation_summary() -> str | None:
    args = sys.argv[2:]
    if "--run" not in args:
        return None

    index = args.index("--run")
    if index + 1 >= len(args):
        print("Usage: python main.py recommendation-summary [--run <run_id>]")
        return ""
    run_id = args[index + 1].strip()
    if not run_id:
        print("Usage: python main.py recommendation-summary [--run <run_id>]")
        return ""
    return run_id


def _parse_run_filter_for_recommendation_actions() -> str | None:
    args = sys.argv[2:]
    if "--run" not in args:
        return None

    index = args.index("--run")
    if index + 1 >= len(args):
        print("Usage: python main.py recommendation-actions [--run <run_id>]")
        return ""
    run_id = args[index + 1].strip()
    if not run_id:
        print("Usage: python main.py recommendation-actions [--run <run_id>]")
        return ""
    return run_id


def _parse_run_filter_for_recommendation_proposals() -> str | None:
    args = sys.argv[2:]
    if "--run" not in args:
        return None

    index = args.index("--run")
    if index + 1 >= len(args):
        print("Usage: python main.py recommendation-proposals [--run <run_id>]")
        return ""
    run_id = args[index + 1].strip()
    if not run_id:
        print("Usage: python main.py recommendation-proposals [--run <run_id>]")
        return ""
    return run_id


def _parse_run_filter_for_recommendation_drafts() -> str | None:
    args = sys.argv[2:]
    if "--run" not in args:
        return None

    index = args.index("--run")
    if index + 1 >= len(args):
        print("Usage: python main.py recommendation-drafts [--run <run_id>]")
        return ""
    run_id = args[index + 1].strip()
    if not run_id:
        print("Usage: python main.py recommendation-drafts [--run <run_id>]")
        return ""
    return run_id


def _parse_run_filter_for_recommendation_outcomes() -> str | None:
    args = sys.argv[2:]
    if "--run" not in args:
        return None

    index = args.index("--run")
    if index + 1 >= len(args):
        print("Usage: python main.py recommendation-outcomes [--run <run_id>]")
        return ""
    run_id = args[index + 1].strip()
    if not run_id:
        print("Usage: python main.py recommendation-outcomes [--run <run_id>]")
        return ""
    return run_id


def _parse_run_filter_for_recommendation_resolution() -> str | None:
    args = sys.argv[2:]
    if "--run" not in args:
        return None

    index = args.index("--run")
    if index + 1 >= len(args):
        print("Usage: python main.py recommendation-resolution [--run <run_id>]")
        return ""
    run_id = args[index + 1].strip()
    if not run_id:
        print("Usage: python main.py recommendation-resolution [--run <run_id>]")
        return ""
    return run_id


def _parse_recommendation_create_args() -> dict[str, str] | None:
    args = sys.argv[2:]
    usage = "Usage: python main.py recommendation-create --reviewer-task <reviewer_task_id> [--run <run_id>]"
    if "--reviewer-task" not in args:
        print(usage)
        return None

    reviewer_index = args.index("--reviewer-task")
    if reviewer_index + 1 >= len(args):
        print(usage)
        return None
    reviewer_task_id = args[reviewer_index + 1].strip()
    if not reviewer_task_id:
        print(usage)
        return None

    run_id = None
    if "--run" in args:
        run_index = args.index("--run")
        if run_index + 1 >= len(args):
            print(usage)
            return None
        run_id = args[run_index + 1].strip()
        if not run_id:
            print(usage)
            return None

    return {"reviewer_task_id": reviewer_task_id, "run_id": run_id}


def _parse_recommendation_archive_args() -> dict[str, str | None] | None:
    args = sys.argv[2:]
    usage = (
        "Usage: python main.py recommendation-archive "
        "--reviewer-task <reviewer_task_id> [--run <run_id>]"
    )
    if "--reviewer-task" not in args:
        print(usage)
        return None

    reviewer_index = args.index("--reviewer-task")
    if reviewer_index + 1 >= len(args):
        print(usage)
        return None
    reviewer_task_id = args[reviewer_index + 1].strip()
    if not reviewer_task_id:
        print(usage)
        return None

    run_id = None
    if "--run" in args:
        run_index = args.index("--run")
        if run_index + 1 >= len(args):
            print(usage)
            return None
        run_id = args[run_index + 1].strip()
        if not run_id:
            print(usage)
            return None

    return {"reviewer_task_id": reviewer_task_id, "run_id": run_id}


def _parse_recommendation_accept_args() -> dict[str, str | None] | None:
    args = sys.argv[2:]
    usage = (
        "Usage: python main.py recommendation-accept "
        "--reviewer-task <reviewer_task_id> [--run <run_id>]"
    )
    if "--reviewer-task" not in args:
        print(usage)
        return None

    reviewer_index = args.index("--reviewer-task")
    if reviewer_index + 1 >= len(args):
        print(usage)
        return None
    reviewer_task_id = args[reviewer_index + 1].strip()
    if not reviewer_task_id:
        print(usage)
        return None

    run_id = None
    if "--run" in args:
        run_index = args.index("--run")
        if run_index + 1 >= len(args):
            print(usage)
            return None
        run_id = args[run_index + 1].strip()
        if not run_id:
            print(usage)
            return None

    return {"reviewer_task_id": reviewer_task_id, "run_id": run_id}


def _parse_run_filter_for_recommendation_lineage() -> str | None:
    args = sys.argv[2:]
    if "--run" not in args:
        return None

    index = args.index("--run")
    if index + 1 >= len(args):
        print("Usage: python main.py recommendation-lineage [--run <run_id>]")
        return ""
    run_id = args[index + 1].strip()
    if not run_id:
        print("Usage: python main.py recommendation-lineage [--run <run_id>]")
        return ""
    return run_id


def _parse_run_filter_for_recommendation_created_tasks() -> str | None:
    args = sys.argv[2:]
    if "--run" not in args:
        return None

    index = args.index("--run")
    if index + 1 >= len(args):
        print("Usage: python main.py recommendation-created-tasks [--run <run_id>]")
        return ""
    run_id = args[index + 1].strip()
    if not run_id:
        print("Usage: python main.py recommendation-created-tasks [--run <run_id>]")
        return ""
    return run_id


def _parse_recommendation_confirm_args() -> str | None:
    args = sys.argv[2:]
    usage = "Usage: python main.py recommendation-confirm --task <task_id>"
    if "--task" not in args:
        print(usage)
        return None

    index = args.index("--task")
    if index + 1 >= len(args):
        print(usage)
        return None

    task_id = args[index + 1].strip()
    if not task_id:
        print(usage)
        return None
    return task_id


def _parse_create_followup_review_args() -> str | None:
    args = sys.argv[2:]
    usage = "Usage: python main.py create-followup-review --task <task_id>"
    if "--task" not in args:
        print(usage)
        return None

    index = args.index("--task")
    if index + 1 >= len(args):
        print(usage)
        return None

    task_id = args[index + 1].strip()
    if not task_id:
        print(usage)
        return None
    return task_id


def _parse_create_repair_task_args() -> str | None:
    args = sys.argv[2:]
    usage = "Usage: python main.py create-repair-task --task <task_id>"
    if "--task" not in args:
        print(usage)
        return None

    index = args.index("--task")
    if index + 1 >= len(args):
        print(usage)
        return None

    task_id = args[index + 1].strip()
    if not task_id:
        print(usage)
        return None
    return task_id


def _parse_execute_ready_candidate_args() -> dict[str, str] | None:
    args = sys.argv[2:]
    usage = "Usage: python main.py execute-ready-candidate --task <task_id> [--provider <provider_name>]"
    if "--task" not in args:
        print(usage)
        return None

    index = args.index("--task")
    if index + 1 >= len(args):
        print(usage)
        return None

    task_id = args[index + 1].strip()
    if not task_id:
        print(usage)
        return None

    provider = "mock"
    if "--provider" in args:
        provider_index = args.index("--provider")
        if provider_index + 1 >= len(args):
            print(usage)
            return None
        provider = args[provider_index + 1].strip()
        if not provider:
            print(usage)
            return None

    return {"task_id": task_id, "provider": provider}


def _parse_run_filter_for_confirmed_recommendation_tasks() -> str | None:
    args = sys.argv[2:]
    if "--run" not in args:
        return None

    index = args.index("--run")
    if index + 1 >= len(args):
        print("Usage: python main.py confirmed-recommendation-tasks [--run <run_id>]")
        return ""
    run_id = args[index + 1].strip()
    if not run_id:
        print("Usage: python main.py confirmed-recommendation-tasks [--run <run_id>]")
        return ""
    return run_id


def _parse_run_filter_for_ready_recommendation_tasks() -> str | None:
    args = sys.argv[2:]
    if "--run" not in args:
        return None

    index = args.index("--run")
    if index + 1 >= len(args):
        print("Usage: python main.py ready-recommendation-tasks [--run <run_id>]")
        return ""
    run_id = args[index + 1].strip()
    if not run_id:
        print("Usage: python main.py ready-recommendation-tasks [--run <run_id>]")
        return ""
    return run_id


def _parse_run_filter_for_ready_execution_candidates() -> str | None:
    args = sys.argv[2:]
    if "--run" not in args:
        return None

    index = args.index("--run")
    if index + 1 >= len(args):
        print("Usage: python main.py ready-execution-candidates [--run <run_id>]")
        return ""
    run_id = args[index + 1].strip()
    if not run_id:
        print("Usage: python main.py ready-execution-candidates [--run <run_id>]")
        return ""
    return run_id



def _parse_run_filter_for_case_packet_task_execution_candidates() -> str | None:
    args = sys.argv[2:]
    if "--run" not in args:
        return None

    index = args.index("--run")
    if index + 1 >= len(args):
        print("Usage: python main.py case-packet-task-execution-candidates [--run <run_id>]")
        return ""
    run_id = args[index + 1].strip()
    if not run_id:
        print("Usage: python main.py case-packet-task-execution-candidates [--run <run_id>]")
        return ""
    return run_id

def _parse_run_filter_for_recommendation_execution_results() -> str | None:
    args = sys.argv[2:]
    if "--run" not in args:
        return None

    index = args.index("--run")
    if index + 1 >= len(args):
        print("Usage: python main.py recommendation-execution-results [--run <run_id>]")
        return ""
    run_id = args[index + 1].strip()
    if not run_id:
        print("Usage: python main.py recommendation-execution-results [--run <run_id>]")
        return ""
    return run_id


def _parse_recommendation_result_options_selector() -> dict[str, str] | None:
    args = sys.argv[2:]
    usage = (
        "Usage: python main.py recommendation-result-options "
        "[--run <run_id> | --task <task_id>]"
    )
    has_run = "--run" in args
    has_task = "--task" in args

    if has_run and has_task:
        print(usage)
        return None

    if has_task:
        index = args.index("--task")
        if index + 1 >= len(args):
            print(usage)
            return None
        task_id = args[index + 1].strip()
        if not task_id:
            print(usage)
            return None
        return {"scope": "task", "task_id": task_id}

    if has_run:
        index = args.index("--run")
        if index + 1 >= len(args):
            print(usage)
            return None
        run_id = args[index + 1].strip()
        if not run_id:
            print(usage)
            return None
        return {"scope": "run", "run_id": run_id}

    return {"scope": "active"}


def _result_options_for_status(status: str) -> list[str]:
    if status == "completed":
        return [
            "No immediate follow-up required.",
            "Review result if desired.",
        ]
    if status == "needs_review":
        return [
            "Inspect result.",
            "Create follow-up review task explicitly if needed.",
        ]
    if status == "verification_failed":
        return [
            "Inspect failure details.",
            "Create repair task explicitly if needed.",
        ]
    if status == "execution_failed":
        return [
            "Inspect execution failure.",
            "Create repair task explicitly if needed.",
        ]
    return [
        "Inspect result details.",
        "Decide follow-up explicitly if needed.",
    ]


def print_recommendations() -> None:
    run_id = _parse_run_filter_for_recommendations()
    if run_id == "":
        return
    cli_print_recommendations(run_id)


def print_recommendation_summary() -> None:
    run_id = _parse_run_filter_for_recommendation_summary()
    if run_id == "":
        return
    cli_print_recommendation_summary(run_id)


def print_recommendation_actions() -> None:
    run_id = _parse_run_filter_for_recommendation_actions()
    if run_id == "":
        return
    cli_print_recommendation_actions(run_id)


def print_recommendation_proposals() -> None:
    run_id = _parse_run_filter_for_recommendation_proposals()
    if run_id == "":
        return

    if run_id is None:
        state = load_state()
        active_run_id = state.get("active_run_id")
        if not active_run_id:
            print("No active run. Use --run <run_id> or create/select an active run.")
            return
        run_id = str(active_run_id)

    records = load_recommendation_records_for_run(run_id)
    actionable_types = ("repair_candidate", "manual_followup")
    grouped: dict[str, list[dict]] = {rec_type: [] for rec_type in actionable_types}
    for record in records:
        recommendation = record.get("recommendation", {})
        rec_type = str(recommendation.get("recommendation_type", "")).strip()
        if rec_type in grouped:
            grouped[rec_type].append(record)

    print(f"Recommendation proposals for run: {run_id}")
    print(f"Total recommendation records: {len(records)}")
    print("Draft proposals only. No tasks are created by this command.")

    if not grouped["repair_candidate"] and not grouped["manual_followup"]:
        print("No draft proposals generated from actionable recommendation records.")
        return

    defaults = {
        "repair_candidate": {"role": "coder", "title_prefix": "Repair follow-up for"},
        "manual_followup": {"role": "reviewer", "title_prefix": "Manual follow-up for"},
    }

    for rec_type in actionable_types:
        items = grouped[rec_type]
        if not items:
            continue
        print(f"{rec_type} proposals ({len(items)}):")
        for item in items:
            recommendation = item.get("recommendation", {})
            source_task_id = recommendation.get("source_task_id")
            source_artifact_id = recommendation.get("source_artifact_id")
            reason = recommendation.get("reason")
            default = defaults[rec_type]
            title = f"{default['title_prefix']} {source_task_id}"
            role = default["role"]
            print(
                f"- proposed_title={title} "
                f"proposed_role={role} "
                f"source_task_id={source_task_id} "
                f"source_artifact_id={source_artifact_id} "
                f"recommendation_type={rec_type} "
                f"reason={reason}"
            )


def print_recommendation_drafts() -> None:
    run_id = _parse_run_filter_for_recommendation_drafts()
    if run_id == "":
        return
    cli_print_recommendation_drafts(run_id)


def print_recommendation_outcomes() -> None:
    run_id = _parse_run_filter_for_recommendation_outcomes()
    if run_id == "":
        return
    cli_print_recommendation_outcomes(run_id)


def print_recommendation_resolution() -> None:
    run_id = _parse_run_filter_for_recommendation_resolution()
    if run_id == "":
        return
    cli_print_recommendation_resolution(run_id)


def archive_recommendation() -> None:
    parsed = _parse_recommendation_archive_args()
    if parsed is None:
        return

    reviewer_task_id = str(parsed["reviewer_task_id"])
    run_id = parsed.get("run_id")
    cli_archive_recommendation(reviewer_task_id=reviewer_task_id, run_id=run_id)


def accept_recommendation() -> None:
    parsed = _parse_recommendation_accept_args()
    if parsed is None:
        return

    reviewer_task_id = str(parsed["reviewer_task_id"])
    run_id = parsed.get("run_id")
    cli_accept_recommendation(reviewer_task_id=reviewer_task_id, run_id=run_id)


def create_recommendation_task() -> None:
    parsed = _parse_recommendation_create_args()
    if parsed is None:
        return

    reviewer_task_id = parsed["reviewer_task_id"]
    run_id = parsed.get("run_id")

    if not run_id:
        state = load_state()
        active_run_id = state.get("active_run_id")
        if not active_run_id:
            print("No active run. Use --run <run_id> or create/select an active run.")
            return
        run_id = str(active_run_id)

    records = load_recommendation_records_for_run(run_id)
    matches = [
        record
        for record in records
        if str(record.get("reviewer_task_id", "")).strip() == reviewer_task_id
    ]

    if not matches:
        print(
            "No matching recommendation record found for "
            f"reviewer_task_id={reviewer_task_id} in run={run_id}. No task created."
        )
        return

    if len(matches) > 1:
        print(
            "Multiple recommendation records matched this reviewer task in the selected run. "
            "No task created."
        )
        return

    selected = matches[0]
    recommendation = selected.get("recommendation", {})
    recommendation_type = str(recommendation.get("recommendation_type", "")).strip()
    recommendation_reason = str(recommendation.get("reason", "")).strip()

    if recommendation_type == "accept_result":
        print(
            "Recommendation type accept_result does not support task creation. "
            "No task created."
        )
        return

    if recommendation_type not in {"manual_followup", "repair_candidate"}:
        print(
            "Unsupported recommendation type for explicit creation: "
            f"{recommendation_type or '(missing)'}. No task created."
        )
        return

    try:
        reviewer_task = load_task(reviewer_task_id)
    except FileNotFoundError:
        print(f"Reviewer task not found: {reviewer_task_id}. No task created.")
        return

    source_task_id = str(recommendation.get("source_task_id", "")).strip() or str(
        reviewer_task.source_task_id or ""
    ).strip()
    source_artifact_id = str(recommendation.get("source_artifact_id", "")).strip() or str(
        reviewer_task.source_artifact_id or ""
    ).strip()

    if not source_task_id:
        print(
            "Recommendation creation requires source task linkage, but none was found. "
            "No task created."
        )
        return

    try:
        source_task = load_task(source_task_id)
    except FileNotFoundError:
        print(f"Source task not found: {source_task_id}. No task created.")
        return

    if recommendation_type == "manual_followup":
        task = create_followup_review_task_from_needs_review_result(source_task)
    else:
        task = create_repair_task_from_failed_result(source_task)

    updated = False
    if source_artifact_id and not task.source_artifact_id:
        task.source_artifact_id = source_artifact_id
        updated = True
    if recommendation_reason:
        prior_reason = (task.recommendation_reason or "").strip()
        if not prior_reason:
            task.recommendation_reason = recommendation_reason
            updated = True
        elif recommendation_reason not in prior_reason:
            task.recommendation_reason = (
                f"{prior_reason} Reviewer recommendation rationale: {recommendation_reason}"
            )
            updated = True
    if updated:
        save_task(task)

    print("Created task from recommendation-backed draft.")
    print(f"Task ID: {task.id}")
    print(f"Run ID: {task.run_id}")
    print(f"Title: {task.title}")
    print(f"Role: {task.role}")
    print(f"Status: {task.status}")
    print(f"Recommendation Type: {recommendation_type}")
    print(f"Reviewer Task ID: {reviewer_task_id}")
    print(f"Source Task ID: {task.source_task_id}")
    print(f"Source Artifact ID: {task.source_artifact_id}")
    print(f"Recommendation Timestamp: {selected.get('timestamp')}")


def print_recommendation_lineage() -> None:
    run_id = _parse_run_filter_for_recommendation_lineage()
    if run_id == "":
        return

    if run_id is None:
        state = load_state()
        active_run_id = state.get("active_run_id")
        if not active_run_id:
            print("No active run. Use --run <run_id> or create/select an active run.")
            return
        run_id = str(active_run_id)

    lineage_tasks = _load_recommendation_created_tasks_for_run(run_id)

    print(f"Recommendation lineage for run: {run_id}")
    print(f"Recommendation-created tasks: {len(lineage_tasks)}")

    if not lineage_tasks:
        print("No recommendation-created tasks found for this run.")
        return

    for task in lineage_tasks:
        recommendation_type = get_task_recommendation_type(task)
        recommendation_reason = get_task_recommendation_reason(task)
        print("---")
        print(f"Task ID: {task.id}")
        print(f"Title: {task.title}")
        print(f"Role: {task.role}")
        print(f"Status: {task.status}")
        print(f"Source Task ID: {task.source_task_id}")
        print(f"Source Artifact ID: {task.source_artifact_id}")
        if recommendation_type:
            print(f"Recommendation Type: {recommendation_type}")
        if recommendation_reason:
            print(f"Recommendation Reason: {recommendation_reason}")
        elif task.review_reason:
            print(f"Review Reason: {task.review_reason}")


def print_recommendation_created_tasks() -> None:
    run_id = _parse_run_filter_for_recommendation_created_tasks()
    if run_id == "":
        return

    if run_id is None:
        state = load_state()
        active_run_id = state.get("active_run_id")
        if not active_run_id:
            print("No active run. Use --run <run_id> or create/select an active run.")
            return
        run_id = str(active_run_id)

    created_tasks = _load_recommendation_created_tasks_for_run(run_id)

    print(f"Recommendation-created tasks for run: {run_id}")
    print(f"Count: {len(created_tasks)}")

    if not created_tasks:
        print("No recommendation-created tasks found for this run.")
        return

    for task in created_tasks:
        recommendation_type = get_task_recommendation_type(task)
        recommendation_reason = get_task_recommendation_reason(task)

        print("---")
        print(f"Task ID: {task.id}")
        print(f"Title: {task.title}")
        print(f"Role: {task.role}")
        print(f"Status: {task.status}")
        print(f"Success Criteria: {task.success_criteria}")
        print(f"Source Task ID: {task.source_task_id}")
        print(f"Source Artifact ID: {task.source_artifact_id}")
        if recommendation_type:
            print(f"Recommendation Type: {recommendation_type}")
        if recommendation_reason:
            print(f"Recommendation Reason: {recommendation_reason}")
        elif task.review_reason:
            print(f"Review Reason: {task.review_reason}")


def print_confirmed_recommendation_tasks() -> None:
    run_id = _parse_run_filter_for_confirmed_recommendation_tasks()
    if run_id == "":
        return

    if run_id is None:
        state = load_state()
        active_run_id = state.get("active_run_id")
        if not active_run_id:
            print("No active run. Use --run <run_id> or create/select an active run.")
            return
        run_id = str(active_run_id)

    confirmed_tasks = load_confirmed_recommendation_created_tasks_for_run(run_id)

    print(f"Confirmed recommendation-created tasks for run: {run_id}")
    print(f"Count: {len(confirmed_tasks)}")

    if not confirmed_tasks:
        print("No confirmed recommendation-created tasks found for this run.")
        return

    for task in confirmed_tasks:
        recommendation_type = get_task_recommendation_type(task)
        print("---")
        print(f"Task ID: {task.id}")
        print(f"Title: {task.title}")
        print(f"Role: {task.role}")
        print(f"Status: {task.status}")
        print(f"Recommendation Confirmed: {task.recommendation_confirmed}")
        print(f"Source Task ID: {task.source_task_id}")
        print(f"Source Artifact ID: {task.source_artifact_id}")
        if recommendation_type:
            print(f"Recommendation Type: {recommendation_type}")
        if task.recommendation_confirmed_at:
            print(f"Recommendation Confirmed At: {task.recommendation_confirmed_at}")


def print_ready_recommendation_tasks() -> None:
    run_id = _parse_run_filter_for_ready_recommendation_tasks()
    if run_id == "":
        return

    if run_id is None:
        state = load_state()
        active_run_id = state.get("active_run_id")
        if not active_run_id:
            print("No active run. Use --run <run_id> or create/select an active run.")
            return
        run_id = str(active_run_id)

    ready_tasks = _load_ready_recommendation_tasks_for_run(run_id)
    print(f"Ready recommendation-created tasks for run: {run_id}")
    print(f"Count: {len(ready_tasks)}")

    if not ready_tasks:
        print("No ready recommendation-created tasks found for this run.")
        return

    for task in ready_tasks:
        recommendation_type = get_task_recommendation_type(task)
        print("---")
        print(f"Task ID: {task.id}")
        print(f"Title: {task.title}")
        print(f"Role: {task.role}")
        print(f"Status: {task.status}")
        print(f"Recommendation Confirmed: {task.recommendation_confirmed}")
        print(f"Source Task ID: {task.source_task_id}")
        print(f"Source Artifact ID: {task.source_artifact_id}")
        if recommendation_type:
            print(f"Recommendation Type: {recommendation_type}")
        if task.recommendation_confirmed_at:
            print(f"Recommendation Confirmed At: {task.recommendation_confirmed_at}")
        if task.success_criteria:
            print(f"Success Criteria: {task.success_criteria}")


def print_ready_execution_candidates() -> None:
    run_id = _parse_run_filter_for_ready_execution_candidates()
    if run_id == "":
        return

    if run_id is None:
        state = load_state()
        active_run_id = state.get("active_run_id")
        if not active_run_id:
            print("No active run. Use --run <run_id> or create/select an active run.")
            return
        run_id = str(active_run_id)

    candidate_tasks = _load_ready_execution_candidates_for_run(run_id)
    print(f"Ready execution candidates for run: {run_id}")
    print(f"Count: {len(candidate_tasks)}")
    print("These tasks are eligible for explicit operator-chosen execution consideration.")
    print("This command does not execute tasks and does not change queue behavior.")

    if not candidate_tasks:
        print("No ready execution candidates found for this run.")
        return

    for task in candidate_tasks:
        recommendation_type = get_task_recommendation_type(task)
        print("---")
        print(f"Task ID: {task.id}")
        print(f"Title: {task.title}")
        print(f"Role: {task.role}")
        print(f"Status: {task.status}")
        print(f"Source Task ID: {task.source_task_id}")
        print(f"Source Artifact ID: {task.source_artifact_id}")
        if recommendation_type:
            print(f"Recommendation Type: {recommendation_type}")
        if task.recommendation_confirmed_at:
            print(f"Recommendation Confirmed At: {task.recommendation_confirmed_at}")
        if task.success_criteria:
            print(f"Success Criteria: {task.success_criteria}")



def print_case_packet_task_execution_candidates() -> None:
    run_id = _parse_run_filter_for_case_packet_task_execution_candidates()
    if run_id == "":
        return

    if run_id is None:
        state = load_state()
        active_run_id = state.get("active_run_id")
        if not active_run_id:
            print("No active run. Use --run <run_id> or create/select an active run.")
            return
        run_id = str(active_run_id)

    result = surface_case_packet_task_execution_candidates(run_id)
    print(json.dumps(result, indent=2))

def print_recommendation_execution_results() -> None:
    run_id = _parse_run_filter_for_recommendation_execution_results()
    if run_id == "":
        return

    if run_id is None:
        state = load_state()
        active_run_id = state.get("active_run_id")
        if not active_run_id:
            print("No active run. Use --run <run_id> or create/select an active run.")
            return
        run_id = str(active_run_id)

    executed_tasks = load_post_execution_recommendation_result_tasks_for_run(run_id)
    print(f"Recommendation execution results for run: {run_id}")
    print(f"Executed recommendation-derived tasks: {len(executed_tasks)}")
    print("These are post-execution results for recommendation-derived follow-up work.")
    print("This command does not execute, reroute, or change queue behavior.")

    if not executed_tasks:
        print("No executed recommendation-derived tasks found for this run.")
        return

    for task in executed_tasks:
        recommendation_type = get_task_recommendation_type(task)
        recommendation_reason = get_task_recommendation_reason(task)
        print("---")
        print(f"Task ID: {task.id}")
        print(f"Title: {task.title}")
        print(f"Role: {task.role}")
        print(f"Final Status: {task.status}")
        print(f"Source Task ID: {task.source_task_id}")
        print(f"Source Artifact ID: {task.source_artifact_id}")
        if recommendation_type:
            print(f"Recommendation Type: {recommendation_type}")
        if recommendation_reason:
            print(f"Recommendation Reason: {recommendation_reason}")
        if task.recommendation_confirmed_at:
            print(f"Recommendation Confirmed At: {task.recommendation_confirmed_at}")
        if task.success_criteria:
            print(f"Success Criteria: {task.success_criteria}")


def print_recommendation_result_options() -> None:
    selector = _parse_recommendation_result_options_selector()
    if selector is None:
        return

    scope = selector["scope"]
    context_label = ""
    scoped_tasks = []

    if scope == "task":
        task_id = selector["task_id"]
        try:
            task = load_task(task_id)
        except FileNotFoundError:
            print(f"Task not found: {task_id}")
            return
        context_label = f"Task: {task_id}"
        if is_post_execution_recommendation_result_task(task):
            scoped_tasks = [task]
    else:
        if scope == "run":
            run_id = selector["run_id"]
        else:
            state = load_state()
            active_run_id = state.get("active_run_id")
            if not active_run_id:
                print("No active run. Use --run <run_id>, --task <task_id>, or create/select an active run.")
                return
            run_id = str(active_run_id)

        context_label = f"Run: {run_id}"
        scoped_tasks = load_post_execution_recommendation_result_tasks_for_run(run_id)

    print(f"Recommendation result options ({context_label})")
    print(f"Post-execution recommendation-derived results: {len(scoped_tasks)}")
    print("This command is read-only and does not execute responses or change queue behavior.")

    if not scoped_tasks:
        print("No post-execution recommendation-derived results found for this scope.")
        return

    for task in scoped_tasks:
        recommendation_type = get_task_recommendation_type(task)
        print("---")
        print(f"Task ID: {task.id}")
        print(f"Title: {task.title}")
        print(f"Role: {task.role}")
        print(f"Final Status: {task.status}")
        print(f"Source Task ID: {task.source_task_id}")
        print(f"Source Artifact ID: {task.source_artifact_id}")
        if recommendation_type:
            print(f"Recommendation Type: {recommendation_type}")
        print("Operator Response Options:")
        for option in _result_options_for_status(task.status):
            print(f"- {option}")


def confirm_recommendation_task() -> None:
    task_id = _parse_recommendation_confirm_args()
    if task_id is None:
        return

    try:
        task = load_task(task_id)
    except FileNotFoundError:
        print(f"Task not found: {task_id}")
        return

    if not is_recommendation_created_task(task):
        print(f"Task is not recommendation-created and cannot be confirmed: {task_id}")
        return

    if task.recommendation_confirmed:
        print("Task is already recommendation-confirmed.")
        print(f"Task ID: {task.id}")
        print(f"Title: {task.title}")
        print(f"Role: {task.role}")
        print(f"Status: {task.status}")
        print(f"Recommendation Confirmed: {task.recommendation_confirmed}")
        if task.recommendation_confirmed_at:
            print(f"Recommendation Confirmed At: {task.recommendation_confirmed_at}")
        return

    task.recommendation_confirmed = True
    task.recommendation_confirmed_at = datetime.now(timezone.utc).isoformat()
    save_task(task)

    print("Recommendation-created task confirmed.")
    print(f"Task ID: {task.id}")
    print(f"Title: {task.title}")
    print(f"Role: {task.role}")
    print(f"Status: {task.status}")
    print(f"Recommendation Confirmed: {task.recommendation_confirmed}")
    print(f"Recommendation Confirmed At: {task.recommendation_confirmed_at}")


def create_followup_review() -> None:
    task_id = _parse_create_followup_review_args()
    if task_id is None:
        return

    try:
        source_task = load_task(task_id)
    except FileNotFoundError:
        print(f"Task not found: {task_id}")
        return

    if not is_recommendation_created_task(source_task):
        print(f"Task is not recommendation-derived: {task_id}")
        return
    if not is_post_execution_recommendation_result_task(source_task):
        print(f"Task is not post-execution recommendation-derived: {task_id}")
        return
    if source_task.status != "needs_review":
        print(f"Task status is not needs_review: {task_id} (status={source_task.status})")
        return

    existing = find_live_response_task_duplicate(
        run_id=source_task.run_id,
        source_task_id=source_task.id,
        recommendation_type="manual_followup",
    )
    if existing is not None:
        print("Equivalent follow-up review task already exists; no new task created.")
        print(f"Existing Task ID: {existing.id}")
        print(f"Existing Title: {existing.title}")
        print(f"Existing Status: {existing.status}")
        return

    followup_task = create_followup_review_task_from_needs_review_result(source_task)
    print("Created follow-up review task.")
    print(f"Task ID: {followup_task.id}")
    print(f"Run ID: {followup_task.run_id}")
    print(f"Title: {followup_task.title}")
    print(f"Role: {followup_task.role}")
    print(f"Status: {followup_task.status}")
    print(f"Source Task ID: {followup_task.source_task_id}")
    print(f"Source Artifact ID: {followup_task.source_artifact_id}")
    print(f"Needs-Review Result Artifact ID: {source_task.execution_artifact_id}")
    print("Created from needs_review recommendation-derived result.")


def create_repair_task() -> None:
    task_id = _parse_create_repair_task_args()
    if task_id is None:
        return

    try:
        source_task = load_task(task_id)
    except FileNotFoundError:
        print(f"Task not found: {task_id}")
        return

    if not is_recommendation_created_task(source_task):
        print(f"Task is not recommendation-derived: {task_id}")
        return
    if not is_post_execution_recommendation_result_task(source_task):
        print(f"Task is not post-execution recommendation-derived: {task_id}")
        return
    if source_task.status not in {"verification_failed", "execution_failed"}:
        print(
            "Task status is not eligible for repair-task creation: "
            f"{task_id} (status={source_task.status})"
        )
        return

    existing = find_live_response_task_duplicate(
        run_id=source_task.run_id,
        source_task_id=source_task.id,
        recommendation_type="repair_candidate",
    )
    if existing is not None:
        print("Equivalent repair task already exists; no new task created.")
        print(f"Existing Task ID: {existing.id}")
        print(f"Existing Title: {existing.title}")
        print(f"Existing Status: {existing.status}")
        return

    repair_task = create_repair_task_from_failed_result(source_task)
    print("Created repair task.")
    print(f"Task ID: {repair_task.id}")
    print(f"Run ID: {repair_task.run_id}")
    print(f"Title: {repair_task.title}")
    print(f"Role: {repair_task.role}")
    print(f"Status: {repair_task.status}")
    print(f"Source Task ID: {repair_task.source_task_id}")
    print(f"Source Artifact ID: {repair_task.source_artifact_id}")
    print(f"Failed Result Artifact ID: {source_task.execution_artifact_id}")
    print("Created from failed recommendation-derived result.")


def execute_ready_candidate() -> None:
    parsed = _parse_execute_ready_candidate_args()
    if parsed is None:
        return
    task_id = parsed["task_id"]
    provider_name = parsed["provider"]

    try:
        task = load_task(task_id)
    except FileNotFoundError:
        print(f"Task not found: {task_id}")
        return

    if not is_recommendation_created_task(task):
        print(f"Task is not recommendation-created: {task_id}")
        return
    if not is_ready_recommendation_created_task(task):
        print(f"Task is not ready (recommendation_confirmed is not true): {task_id}")
        return
    if not is_ready_execution_candidate_task(task):
        print(f"Task is not queued and cannot be executed via this command: {task_id}")
        return

    print(f"Executing ready candidate task: {task.id}")
    print(f"Requested provider: {provider_name}")
    process_task_by_id(task=task, provider_name=provider_name)


def main() -> None:
    command = sys.argv[1] if len(sys.argv) > 1 else ""

    if command == "init":
        initialize_workspace()
        return

    if command == "status":
        print_status()
        return

    if command == "new-run":
        create_new_run()
        return

    if command == "next":
        provider = _parse_provider_for_next()
        if not provider:
            return
        process_next_task(provider_name=provider)
        return

    if command == "verify":
        if len(sys.argv) < 4:
            print("Usage: python main.py verify <check_name> <target_path> [text]")
            return
        check_name = sys.argv[2]
        target_path = str(resolve_project_path(sys.argv[3]))
        options = None
        if check_name == "file_contains_text":
            if len(sys.argv) < 5:
                print("Usage: python main.py verify file_contains_text <target_path> <text>")
                return
            options = {"text": sys.argv[4]}
        result = run_check(check_name, target_path, check_options=options)
        print(json.dumps(result.to_dict(), indent=2))
        return

    if command == "intake-judge":
        run_intake_judge()
        return

    if command == "intake-handoff-admit":
        run_intake_handoff_admit()
        return

    if command == "case-packet-seed-review":
        run_case_packet_seed_review()
        return

    if command == "case-packet-creation-authorize":
        run_case_packet_creation_authorize()
        return

    if command == "case-packet-persist-authorized":
        run_case_packet_persist_authorized()
        return

    if command == "case-packet-task-candidate-review":
        run_case_packet_task_candidate_review()
        return

    if command == "case-packet-task-creation-authorize":
        run_case_packet_task_creation_authorize()
        return
    if command == "case-packet-task-create-authorized":
        run_case_packet_task_create_authorized()
        return

    if command == "case-packet-task-execution-candidates":
        print_case_packet_task_execution_candidates()
        return

    if command == "case-packet-task-execution-authorize":
        run_case_packet_task_execution_authorize()
        return

    if command == "case-packet-task-execute-authorized":
        run_case_packet_task_execute_authorized()
        return

    if command == "case-packet-task-execution-result-review":
        run_case_packet_task_execution_result_review()
        return

    if command == "case-packet-task-execution-result-options":
        run_case_packet_task_execution_result_options()
        return

    if command == "current-success-result-review":
        run_current_success_result_review()
        return

    if command == "current-success-result-accept":
        run_current_success_result_accept()
        return

    if command == "case-packet-create":
        run_case_packet_create()
        return

    if command == "case-packet-show":
        run_case_packet_show()
        return

    if command == "case-packet-summary":
        run_case_packet_summary()
        return

    if command == "case-packet-validate":
        run_case_packet_validate()
        return

    if command == "case-packet-init":
        run_case_packet_init()
        return

    if command == "case-packet-append":
        run_case_packet_append()
        return

    if command == "case-packet-orient":
        run_case_packet_orient()
        return

    if command == "recommendations":
        print_recommendations()
        return

    if command == "recommendation-summary":
        print_recommendation_summary()
        return

    if command == "recommendation-actions":
        print_recommendation_actions()
        return

    if command == "recommendation-proposals":
        print_recommendation_proposals()
        return

    if command == "recommendation-drafts":
        print_recommendation_drafts()
        return

    if command == "recommendation-outcomes":
        print_recommendation_outcomes()
        return

    if command == "recommendation-resolution":
        print_recommendation_resolution()
        return

    if command == "recommendation-archive":
        archive_recommendation()
        return

    if command == "recommendation-accept":
        accept_recommendation()
        return

    if command == "recommendation-create":
        create_recommendation_task()
        return

    if command == "recommendation-lineage":
        print_recommendation_lineage()
        return

    if command == "recommendation-created-tasks":
        print_recommendation_created_tasks()
        return

    if command == "recommendation-confirm":
        confirm_recommendation_task()
        return

    if command == "confirmed-recommendation-tasks":
        print_confirmed_recommendation_tasks()
        return

    if command == "ready-recommendation-tasks":
        print_ready_recommendation_tasks()
        return

    if command == "ready-execution-candidates":
        print_ready_execution_candidates()
        return

    if command == "recommendation-execution-results":
        print_recommendation_execution_results()
        return

    if command == "recommendation-result-options":
        print_recommendation_result_options()
        return

    if command == "create-followup-review":
        create_followup_review()
        return

    if command == "create-repair-task":
        create_repair_task()
        return

    if command == "execute-ready-candidate":
        execute_ready_candidate()
        return

    print(
        "Usage: python main.py <init|status|new-run|next|verify|intake-judge|intake-handoff-admit|case-packet-seed-review|case-packet-creation-authorize|case-packet-persist-authorized|case-packet-task-candidate-review|case-packet-task-creation-authorize|case-packet-task-create-authorized|case-packet-task-execution-candidates|case-packet-task-execution-authorize|case-packet-task-execute-authorized|case-packet-task-execution-result-review|case-packet-task-execution-result-options|current-success-result-review|current-success-result-accept|case-packet-create|case-packet-show|case-packet-summary|case-packet-validate|case-packet-init|case-packet-append|case-packet-orient|recommendations|recommendation-summary|recommendation-actions|recommendation-proposals|recommendation-drafts|recommendation-outcomes|recommendation-resolution|recommendation-archive|recommendation-accept|recommendation-create|recommendation-lineage|recommendation-created-tasks|recommendation-confirm|confirmed-recommendation-tasks|ready-recommendation-tasks|ready-execution-candidates|recommendation-execution-results|recommendation-result-options|create-followup-review|create-repair-task|execute-ready-candidate>"
    )


if __name__ == "__main__":
    main()


