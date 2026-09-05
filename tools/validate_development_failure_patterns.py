#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
from pathlib import Path
from typing import Any

SCHEMA_VERSION = "DEVELOPMENT_FAILURE_PATTERN_V1"
REPOSITORY = "BogdanAIP/MimiSeek-review"
PATTERN_ID_RE = re.compile(r"^DFP-[0-9]{4}$")
OCCURRENCE_ID_RE = re.compile(r"^DFP-[0-9]{4}-O[0-9]{3}$")
FAILURE_CLASS_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
LOCATOR_RE = re.compile(r"^(review_comment|issue_comment|review_thread|pr_comment):.+$")
REGULAR_GIT_MODES = {"100644", "100755"}

TOP_FIELDS = {
    "schema_version",
    "pattern_id",
    "status",
    "title",
    "failure_class",
    "origin",
    "root_cause",
    "failure_mechanism",
    "violated_invariant",
    "trigger_conditions",
    "applicable_scope",
    "non_applicable_scope",
    "repository_search",
    "prevention",
    "occurrences",
}
ORIGIN_FIELDS = {"source_kind", "repository", "pr", "head_sha", "evidence_locator"}
SEARCH_FIELDS = {"status", "searched_scope", "discovered_instances", "follow_up_refs", "notes"}
PREVENTION_FIELDS = {"kind", "guard_refs", "regression_refs", "manual_only_reason"}
OCCURRENCE_FIELDS = {
    "occurrence_id",
    "relation",
    "pr",
    "head_sha",
    "evidence_locator",
    "prevention_failure_reason",
}
REPEAT_FAILURE_REASONS = {
    "NO_GUARD",
    "GUARD_TOO_NARROW",
    "GUARD_NOT_IN_CI",
    "PATTERN_NOT_RETRIEVED",
    "SCOPE_WRONG",
    "NEW_VARIANT",
    "UNKNOWN_PENDING_ANALYSIS",
}


class DevelopmentFailurePatternError(RuntimeError):
    pass


def require_exact_shape(value: Any, expected: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DevelopmentFailurePatternError(f"{label} must be an object")
    if set(value) != expected:
        missing = sorted(expected - set(value))
        unknown = sorted(set(value) - expected)
        raise DevelopmentFailurePatternError(
            f"{label} shape mismatch; missing={missing} unknown={unknown}"
        )
    return value


def require_nonempty_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DevelopmentFailurePatternError(f"{label} must be a non-empty string")
    return value


def require_positive_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise DevelopmentFailurePatternError(f"{label} must be a positive integer")
    return value


def require_sha(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA40_RE.fullmatch(value):
        raise DevelopmentFailurePatternError(f"{label} must be a lowercase 40-character SHA")
    return value


def require_unique_strings(
    value: Any,
    label: str,
    *,
    allow_empty: bool = False,
) -> list[str]:
    if not isinstance(value, list) or any(
        not isinstance(item, str) or not item.strip() for item in value
    ):
        raise DevelopmentFailurePatternError(f"{label} must be an array of non-empty strings")
    if not allow_empty and not value:
        raise DevelopmentFailurePatternError(f"{label} must not be empty")
    if len(value) != len(set(value)):
        raise DevelopmentFailurePatternError(f"{label} contains duplicates")
    return value


def require_repo_relative(value: str, label: str) -> str:
    raw_path = value.split("#", 1)[0]
    path = Path(raw_path)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise DevelopmentFailurePatternError(f"{label} must be a repository-relative path")
    if path.parts[0] == ".git":
        raise DevelopmentFailurePatternError(f"{label} must not reference .git metadata")
    return path.as_posix()


def tracked_regular_files(root: Path) -> set[str]:
    root = root.resolve()
    try:
        top = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise DevelopmentFailurePatternError(
            "repeat-prevention validation requires an exact Git working tree"
        ) from exc
    if Path(top).resolve() != root:
        raise DevelopmentFailurePatternError(
            f"repeat-prevention root is not the Git toplevel: root={root} git={top}"
        )

    try:
        raw = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-s", "-z"],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise DevelopmentFailurePatternError("cannot resolve tracked Git index entries") from exc

    result: set[str] = set()
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            metadata, path_bytes = record.split(b"\t", 1)
            mode, _blob, stage = metadata.decode("ascii").split()
            path = path_bytes.decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise DevelopmentFailurePatternError(
                "malformed/non-UTF8 tracked Git index entry"
            ) from exc
        if stage != "0":
            raise DevelopmentFailurePatternError(
                f"unmerged Git index entry is not valid repeat-prevention authority: {path}"
            )
        if mode in REGULAR_GIT_MODES:
            result.add(path)
    return result


def require_tracked_regular_ref(
    root: Path,
    value: str,
    label: str,
    tracked: set[str],
) -> str:
    path = require_repo_relative(value, label)
    if path not in tracked:
        raise DevelopmentFailurePatternError(
            f"{label} is not a tracked regular repository file: {path}"
        )
    candidate = root / path
    if candidate.is_symlink() or not candidate.is_file():
        raise DevelopmentFailurePatternError(
            f"{label} checkout path is not a regular file: {path}"
        )
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise DevelopmentFailurePatternError(
            f"{label} tracked file cannot be resolved: {path}"
        ) from exc
    if not resolved.is_relative_to(root.resolve()):
        raise DevelopmentFailurePatternError(
            f"{label} resolves outside repository authority: {path}"
        )
    return path


def validate_origin(value: Any, label: str) -> dict[str, Any]:
    origin = require_exact_shape(value, ORIGIN_FIELDS, label)
    if origin["source_kind"] not in {"REVIEW_FINDING", "PROCESS_INCIDENT"}:
        raise DevelopmentFailurePatternError(f"{label}.source_kind is unsupported")
    if origin["repository"] != REPOSITORY:
        raise DevelopmentFailurePatternError(
            f"{label}.repository must remain scoped to {REPOSITORY}"
        )
    require_positive_int(origin["pr"], f"{label}.pr")
    require_sha(origin["head_sha"], f"{label}.head_sha")
    locator = require_nonempty_string(origin["evidence_locator"], f"{label}.evidence_locator")
    if not LOCATOR_RE.fullmatch(locator):
        raise DevelopmentFailurePatternError(f"{label}.evidence_locator is invalid")
    return origin


def validate_repository_search(
    value: Any,
    root: Path,
    label: str,
    tracked: set[str],
) -> dict[str, Any]:
    search = require_exact_shape(value, SEARCH_FIELDS, label)
    if search["status"] not in {"COMPLETED", "BOUNDED_FOLLOW_UP"}:
        raise DevelopmentFailurePatternError(f"{label}.status is unsupported")
    scopes = require_unique_strings(search["searched_scope"], f"{label}.searched_scope")
    discovered = require_unique_strings(
        search["discovered_instances"], f"{label}.discovered_instances", allow_empty=True
    )
    follow_up = require_unique_strings(
        search["follow_up_refs"], f"{label}.follow_up_refs", allow_empty=True
    )
    require_nonempty_string(search["notes"], f"{label}.notes")

    if search["status"] == "COMPLETED" and follow_up:
        raise DevelopmentFailurePatternError(
            f"{label}.COMPLETED search must not retain follow_up_refs"
        )
    if search["status"] == "BOUNDED_FOLLOW_UP" and not follow_up:
        raise DevelopmentFailurePatternError(
            f"{label}.BOUNDED_FOLLOW_UP requires at least one follow_up_ref"
        )

    for index, pattern in enumerate(scopes, start=1):
        normalized = require_repo_relative(pattern, f"{label}.searched_scope[{index}]")
        matches = sorted(path for path in tracked if fnmatch.fnmatchcase(path, normalized))
        if not matches:
            raise DevelopmentFailurePatternError(
                f"{label}.searched_scope[{index}] matches no tracked regular repository files: {pattern}"
            )
    for index, instance in enumerate(discovered, start=1):
        require_tracked_regular_ref(
            root,
            instance,
            f"{label}.discovered_instances[{index}]",
            tracked,
        )
    return search


def validate_prevention(
    value: Any,
    root: Path,
    label: str,
    tracked: set[str],
) -> dict[str, Any]:
    prevention = require_exact_shape(value, PREVENTION_FIELDS, label)
    kind = prevention["kind"]
    if kind not in {"EXECUTABLE", "MANUAL_ONLY"}:
        raise DevelopmentFailurePatternError(f"{label}.kind is unsupported")
    guards = require_unique_strings(
        prevention["guard_refs"], f"{label}.guard_refs", allow_empty=True
    )
    regressions = require_unique_strings(
        prevention["regression_refs"], f"{label}.regression_refs", allow_empty=True
    )
    reason = prevention["manual_only_reason"]

    if kind == "EXECUTABLE":
        if not guards or not regressions:
            raise DevelopmentFailurePatternError(
                f"{label}.EXECUTABLE requires guard_refs and regression_refs"
            )
        if reason is not None:
            raise DevelopmentFailurePatternError(
                f"{label}.EXECUTABLE requires manual_only_reason=null"
            )
    else:
        if guards or regressions:
            raise DevelopmentFailurePatternError(
                f"{label}.MANUAL_ONLY must not claim executable guard/regression refs"
            )
        require_nonempty_string(reason, f"{label}.manual_only_reason")

    for index, ref in enumerate(guards, start=1):
        require_tracked_regular_ref(root, ref, f"{label}.guard_refs[{index}]", tracked)
    for index, ref in enumerate(regressions, start=1):
        require_tracked_regular_ref(
            root,
            ref,
            f"{label}.regression_refs[{index}]",
            tracked,
        )
    return prevention


def validate_occurrences(
    value: Any,
    pattern_id: str,
    origin: dict[str, Any],
    label: str,
) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise DevelopmentFailurePatternError(f"{label} must be a non-empty array")
    result: list[dict[str, Any]] = []
    seen: set[str] = set()
    previous_id: str | None = None
    origin_count = 0

    for index, raw in enumerate(value, start=1):
        item_label = f"{label}[{index}]"
        item = require_exact_shape(raw, OCCURRENCE_FIELDS, item_label)
        occurrence_id = require_nonempty_string(item["occurrence_id"], f"{item_label}.occurrence_id")
        if not OCCURRENCE_ID_RE.fullmatch(occurrence_id) or not occurrence_id.startswith(
            f"{pattern_id}-O"
        ):
            raise DevelopmentFailurePatternError(
                f"{item_label}.occurrence_id must be namespaced by {pattern_id}"
            )
        if occurrence_id in seen:
            raise DevelopmentFailurePatternError(f"duplicate occurrence_id {occurrence_id}")
        if previous_id is not None and occurrence_id <= previous_id:
            raise DevelopmentFailurePatternError(f"{label} must be ordered by occurrence_id")
        previous_id = occurrence_id
        seen.add(occurrence_id)

        relation = item["relation"]
        if relation not in {"ORIGIN", "REPEAT", "RELATED"}:
            raise DevelopmentFailurePatternError(f"{item_label}.relation is unsupported")
        require_positive_int(item["pr"], f"{item_label}.pr")
        require_sha(item["head_sha"], f"{item_label}.head_sha")
        locator = require_nonempty_string(item["evidence_locator"], f"{item_label}.evidence_locator")
        if not LOCATOR_RE.fullmatch(locator):
            raise DevelopmentFailurePatternError(f"{item_label}.evidence_locator is invalid")

        failure_reason = item["prevention_failure_reason"]
        if relation == "REPEAT":
            if failure_reason not in REPEAT_FAILURE_REASONS:
                raise DevelopmentFailurePatternError(
                    f"{item_label}.REPEAT requires a prevention_failure_reason"
                )
        elif failure_reason is not None:
            raise DevelopmentFailurePatternError(
                f"{item_label}.{relation} requires prevention_failure_reason=null"
            )

        if relation == "ORIGIN":
            origin_count += 1
            if (
                item["pr"] != origin["pr"]
                or item["head_sha"] != origin["head_sha"]
                or item["evidence_locator"] != origin["evidence_locator"]
            ):
                raise DevelopmentFailurePatternError(
                    f"{item_label}.ORIGIN must exactly match the pattern origin"
                )
        result.append(item)

    if result[0]["relation"] != "ORIGIN" or origin_count != 1:
        raise DevelopmentFailurePatternError(
            f"{label} must begin with exactly one ORIGIN occurrence"
        )
    return result


def validate_pattern(
    value: Any,
    root: Path,
    label: str,
    *,
    tracked: set[str] | None = None,
) -> dict[str, Any]:
    if tracked is None:
        tracked = tracked_regular_files(root)
    pattern = require_exact_shape(value, TOP_FIELDS, label)
    if pattern["schema_version"] != SCHEMA_VERSION:
        raise DevelopmentFailurePatternError(f"{label}.schema_version is unsupported")
    pattern_id = require_nonempty_string(pattern["pattern_id"], f"{label}.pattern_id")
    if not PATTERN_ID_RE.fullmatch(pattern_id):
        raise DevelopmentFailurePatternError(f"{label}.pattern_id is invalid")
    if pattern["status"] not in {"ACTIVE", "RETIRED"}:
        raise DevelopmentFailurePatternError(f"{label}.status is unsupported")
    require_nonempty_string(pattern["title"], f"{label}.title")
    failure_class = require_nonempty_string(pattern["failure_class"], f"{label}.failure_class")
    if not FAILURE_CLASS_RE.fullmatch(failure_class):
        raise DevelopmentFailurePatternError(f"{label}.failure_class is invalid")
    origin = validate_origin(pattern["origin"], f"{label}.origin")
    for field in ("root_cause", "failure_mechanism", "violated_invariant"):
        require_nonempty_string(pattern[field], f"{label}.{field}")
    require_unique_strings(pattern["trigger_conditions"], f"{label}.trigger_conditions")
    require_unique_strings(pattern["applicable_scope"], f"{label}.applicable_scope")
    require_unique_strings(
        pattern["non_applicable_scope"], f"{label}.non_applicable_scope", allow_empty=True
    )
    validate_repository_search(
        pattern["repository_search"], root, f"{label}.repository_search", tracked
    )
    validate_prevention(pattern["prevention"], root, f"{label}.prevention", tracked)
    validate_occurrences(pattern["occurrences"], pattern_id, origin, f"{label}.occurrences")
    return pattern


def validate_schema_identity(root: Path) -> None:
    path = root / "data/schemas/development-failure-pattern-v1.schema.json"
    if not path.is_file():
        raise DevelopmentFailurePatternError(f"missing schema file: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    try:
        const = raw["properties"]["schema_version"]["const"]
    except (KeyError, TypeError) as exc:
        raise DevelopmentFailurePatternError(
            "development failure-pattern schema does not expose schema_version const"
        ) from exc
    if const != SCHEMA_VERSION:
        raise DevelopmentFailurePatternError(
            "validator/schema DEVELOPMENT_FAILURE_PATTERN_V1 identity drift"
        )


def load_registry(path: Path, root: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise DevelopmentFailurePatternError(f"missing registry: {path}")
    tracked = tracked_regular_files(root)
    patterns: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    seen_classes: set[str] = set()
    previous_id: str | None = None

    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            raw = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DevelopmentFailurePatternError(
                f"{path}:{line_number}: invalid JSON: {exc.msg}"
            ) from exc
        pattern = validate_pattern(
            raw,
            root,
            f"{path}:{line_number}",
            tracked=tracked,
        )
        pattern_id = pattern["pattern_id"]
        failure_class = pattern["failure_class"]
        if pattern_id in seen_ids:
            raise DevelopmentFailurePatternError(f"duplicate pattern_id {pattern_id}")
        if failure_class in seen_classes:
            raise DevelopmentFailurePatternError(
                f"duplicate failure_class {failure_class}; use occurrences for repeats"
            )
        if previous_id is not None and pattern_id <= previous_id:
            raise DevelopmentFailurePatternError("registry must be ordered by pattern_id")
        previous_id = pattern_id
        seen_ids.add(pattern_id)
        seen_classes.add(failure_class)
        patterns.append(pattern)

    if not patterns:
        raise DevelopmentFailurePatternError(
            "development failure-pattern registry must not be empty"
        )
    return patterns


def active_summary(pattern: dict[str, Any]) -> dict[str, Any]:
    return {
        "pattern_id": pattern["pattern_id"],
        "failure_class": pattern["failure_class"],
        "title": pattern["title"],
        "trigger_conditions": pattern["trigger_conditions"],
        "applicable_scope": pattern["applicable_scope"],
        "search_status": pattern["repository_search"]["status"],
        "follow_up_refs": pattern["repository_search"]["follow_up_refs"],
        "guard_refs": pattern["prevention"]["guard_refs"],
        "regression_refs": pattern["prevention"]["regression_refs"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate MimiSeek self-development repeat-prevention patterns"
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
        help="repository root",
    )
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("data/development-failure-patterns.jsonl"),
        help="registry path relative to --root unless absolute",
    )
    parser.add_argument(
        "--list-active",
        action="store_true",
        help="print compact active-pattern JSON after validation",
    )
    args = parser.parse_args()

    root = args.root.resolve()
    registry = args.registry
    if not registry.is_absolute():
        registry = root / registry

    try:
        validate_schema_identity(root)
        patterns = load_registry(registry, root)
    except (
        DevelopmentFailurePatternError,
        OSError,
        json.JSONDecodeError,
    ) as exc:
        print(f"development failure-pattern validation failed: {exc}")
        return 1

    if args.list_active:
        for pattern in patterns:
            if pattern["status"] == "ACTIVE":
                print(json.dumps(active_summary(pattern), ensure_ascii=False, sort_keys=True))
    else:
        active = sum(pattern["status"] == "ACTIVE" for pattern in patterns)
        print(
            f"development failure-pattern registry valid: patterns={len(patterns)} active={active}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
