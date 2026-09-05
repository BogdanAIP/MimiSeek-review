#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import subprocess
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

SCHEMA_VERSION = "DEVELOPMENT_FAILURE_PATTERN_V1"
REPOSITORY = "BogdanAIP/MimiSeek-review"
REPOSITORY_ISSUE_PREFIX = "https://github.com/BogdanAIP/MimiSeek-review/issues/"
PATTERN_ID_RE = re.compile(r"^DFP-[0-9]{4}$")
OCCURRENCE_ID_RE = re.compile(r"^DFP-[0-9]{4}-O[0-9]{3}$")
FAILURE_CLASS_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
SHA40_RE = re.compile(r"^[0-9a-f]{40}$")
LOCATOR_RE = re.compile(r"^(review_comment|issue_comment|review_thread|pr_comment):.+$")
REGULAR_GIT_MODES = {"100644", "100755"}

TOP_FIELDS = {"schema_version", "pattern_id", "status", "title", "failure_class", "origin", "root_cause", "failure_mechanism", "violated_invariant", "trigger_conditions", "applicable_scope", "non_applicable_scope", "repository_search", "prevention", "occurrences"}
ORIGIN_FIELDS = {"source_kind", "repository", "pr", "head_sha", "evidence_locator"}
SEARCH_FIELDS = {"status", "searched_scope", "discovered_instances", "follow_up_refs", "notes"}
PREVENTION_FIELDS = {"kind", "guard_refs", "regression_refs", "manual_only_reason"}
OCCURRENCE_FIELDS = {"occurrence_id", "relation", "pr", "head_sha", "evidence_locator", "prevention_failure_reason"}
REPEAT_FAILURE_REASONS = {"NO_GUARD", "GUARD_TOO_NARROW", "GUARD_NOT_IN_CI", "PATTERN_NOT_RETRIEVED", "SCOPE_WRONG", "NEW_VARIANT", "UNKNOWN_PENDING_ANALYSIS"}


class DevelopmentFailurePatternError(RuntimeError):
    pass


def exact_object(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DevelopmentFailurePatternError(f"{label} must be an object")
    if set(value) != fields:
        raise DevelopmentFailurePatternError(f"{label} shape mismatch; missing={sorted(fields-set(value))} unknown={sorted(set(value)-fields)}")
    return value


def nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DevelopmentFailurePatternError(f"{label} must be a non-empty string")
    return value


def positive_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise DevelopmentFailurePatternError(f"{label} must be a positive integer")
    return value


def sha40(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA40_RE.fullmatch(value):
        raise DevelopmentFailurePatternError(f"{label} must be a lowercase 40-character SHA")
    return value


def unique_strings(value: Any, label: str, allow_empty: bool=False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
        raise DevelopmentFailurePatternError(f"{label} must be an array of non-empty strings")
    if not allow_empty and not value:
        raise DevelopmentFailurePatternError(f"{label} must not be empty")
    if len(value) != len(set(value)):
        raise DevelopmentFailurePatternError(f"{label} contains duplicates")
    return value


def repo_relative(value: str, label: str) -> str:
    raw = value.split("#",1)[0]
    p = Path(raw)
    if p.is_absolute() or ".." in p.parts or not p.parts:
        raise DevelopmentFailurePatternError(f"{label} must be a repository-relative path")
    if p.parts[0] == ".git":
        raise DevelopmentFailurePatternError(f"{label} must not reference .git metadata")
    return p.as_posix()


def tracked_regular_files(root: Path) -> set[str]:
    root = root.resolve()
    try:
        top = subprocess.run(["git","-C",str(root),"rev-parse","--show-toplevel"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True).stdout.strip()
        if Path(top).resolve() != root:
            raise DevelopmentFailurePatternError(f"repeat-prevention root is not the Git toplevel: root={root} git={top}")
        raw = subprocess.run(["git","-C",str(root),"ls-tree","-r","-z","--full-tree","HEAD"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).stdout
    except (OSError, subprocess.CalledProcessError) as exc:
        raise DevelopmentFailurePatternError("repeat-prevention validation requires an exact Git HEAD tree") from exc
    result: set[str] = set()
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            meta, pbytes = record.split(b"\t",1)
            mode, object_type, _ = meta.decode("ascii").split()
            path = pbytes.decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise DevelopmentFailurePatternError("malformed/non-UTF8 exact HEAD tree entry") from exc
        if mode in REGULAR_GIT_MODES and object_type == "blob":
            result.add(path)
    return result


def tracked_ref(root: Path, value: str, label: str, tracked: set[str]) -> str:
    path = repo_relative(value, label)
    if path not in tracked:
        raise DevelopmentFailurePatternError(f"{label} is not a tracked regular file in exact HEAD: {path}")
    candidate = root / path
    if candidate.is_symlink() or not candidate.is_file():
        raise DevelopmentFailurePatternError(f"{label} checkout path is not a regular file: {path}")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError as exc:
        raise DevelopmentFailurePatternError(f"{label} tracked file cannot be resolved: {path}") from exc
    if not resolved.is_relative_to(root.resolve()):
        raise DevelopmentFailurePatternError(f"{label} resolves outside repository authority: {path}")
    return path


def follow_up_ref(root: Path, value: str, label: str, tracked: set[str]) -> str:
    ref = nonempty(value, label)
    if ref.startswith("https://"):
        parsed = urlparse(ref)
        if parsed.scheme != "https" or parsed.netloc != "github.com" or parsed.query or parsed.fragment or not ref.startswith(REPOSITORY_ISSUE_PREFIX):
            raise DevelopmentFailurePatternError(f"{label} must be an exact MimiSeek issue URL or tracked regular file")
        tail = ref[len(REPOSITORY_ISSUE_PREFIX):]
        if not tail.isdigit() or int(tail) < 1 or "/" in tail:
            raise DevelopmentFailurePatternError(f"{label} must be an exact MimiSeek issue URL or tracked regular file")
        return ref
    try:
        tracked_ref(root, ref, label, tracked)
    except DevelopmentFailurePatternError as exc:
        raise DevelopmentFailurePatternError(
            f"{label} must be an exact MimiSeek issue URL or tracked regular file"
        ) from exc
    return ref


def validate_origin(value: Any, label: str) -> dict[str, Any]:
    origin = exact_object(value, ORIGIN_FIELDS, label)
    if origin["source_kind"] not in {"REVIEW_FINDING", "PROCESS_INCIDENT"}:
        raise DevelopmentFailurePatternError(f"{label}.source_kind is unsupported")
    if origin["repository"] != REPOSITORY:
        raise DevelopmentFailurePatternError(f"{label}.repository must remain scoped to {REPOSITORY}")
    positive_int(origin["pr"], f"{label}.pr"); sha40(origin["head_sha"], f"{label}.head_sha")
    loc = nonempty(origin["evidence_locator"], f"{label}.evidence_locator")
    if not LOCATOR_RE.fullmatch(loc):
        raise DevelopmentFailurePatternError(f"{label}.evidence_locator is invalid")
    return origin


def validate_repository_search(value: Any, root: Path, label: str, tracked: set[str]) -> dict[str, Any]:
    search = exact_object(value, SEARCH_FIELDS, label)
    if search["status"] not in {"COMPLETED", "BOUNDED_FOLLOW_UP"}:
        raise DevelopmentFailurePatternError(f"{label}.status is unsupported")
    scopes = unique_strings(search["searched_scope"], f"{label}.searched_scope")
    discovered = unique_strings(search["discovered_instances"], f"{label}.discovered_instances", allow_empty=True)
    follows = unique_strings(search["follow_up_refs"], f"{label}.follow_up_refs", allow_empty=True)
    nonempty(search["notes"], f"{label}.notes")
    if search["status"] == "COMPLETED" and follows:
        raise DevelopmentFailurePatternError(f"{label}.COMPLETED search must not retain follow_up_refs")
    if search["status"] == "BOUNDED_FOLLOW_UP" and not follows:
        raise DevelopmentFailurePatternError(f"{label}.BOUNDED_FOLLOW_UP requires at least one follow_up_ref")
    for i, pattern in enumerate(scopes, 1):
        normalized = repo_relative(pattern, f"{label}.searched_scope[{i}]")
        if not any(fnmatch.fnmatchcase(p, normalized) for p in tracked):
            raise DevelopmentFailurePatternError(f"{label}.searched_scope[{i}] matches no tracked regular files in exact HEAD: {pattern}")
    for i, instance in enumerate(discovered, 1):
        tracked_ref(root, instance, f"{label}.discovered_instances[{i}]", tracked)
    for i, ref in enumerate(follows, 1):
        follow_up_ref(root, ref, f"{label}.follow_up_refs[{i}]", tracked)
    return search


def validate_prevention(value: Any, root: Path, label: str, tracked: set[str]) -> None:
    p = exact_object(value, PREVENTION_FIELDS, label)
    if p["kind"] not in {"EXECUTABLE", "MANUAL_ONLY"}:
        raise DevelopmentFailurePatternError(f"{label}.kind is unsupported")
    guards = unique_strings(p["guard_refs"], f"{label}.guard_refs", allow_empty=True)
    regressions = unique_strings(p["regression_refs"], f"{label}.regression_refs", allow_empty=True)
    if p["kind"] == "EXECUTABLE":
        if not guards or not regressions:
            raise DevelopmentFailurePatternError(f"{label}.EXECUTABLE requires guard_refs and regression_refs")
        if p["manual_only_reason"] is not None:
            raise DevelopmentFailurePatternError(f"{label}.EXECUTABLE requires manual_only_reason=null")
    else:
        if guards or regressions:
            raise DevelopmentFailurePatternError(f"{label}.MANUAL_ONLY must not claim executable guard/regression refs")
        nonempty(p["manual_only_reason"], f"{label}.manual_only_reason")
    for i, ref in enumerate(guards, 1):
        tracked_ref(root, ref, f"{label}.guard_refs[{i}]", tracked)
    for i, ref in enumerate(regressions, 1):
        tracked_ref(root, ref, f"{label}.regression_refs[{i}]", tracked)


def validate_occurrences(value: Any, pattern_id: str, origin: dict[str, Any], label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or not value:
        raise DevelopmentFailurePatternError(f"{label} must be a non-empty array")
    result: list[dict[str, Any]] = []; seen: set[str] = set(); previous: str | None = None; origin_count = 0
    for i, raw in enumerate(value, 1):
        item_label = f"{label}[{i}]"
        item = exact_object(raw, OCCURRENCE_FIELDS, item_label)
        oid = nonempty(item["occurrence_id"], f"{item_label}.occurrence_id")
        if not OCCURRENCE_ID_RE.fullmatch(oid) or not oid.startswith(f"{pattern_id}-O"):
            raise DevelopmentFailurePatternError(f"{item_label}.occurrence_id must be namespaced by {pattern_id}")
        if oid in seen or (previous is not None and oid <= previous):
            raise DevelopmentFailurePatternError(f"{label} must have unique increasing occurrence_id")
        previous = oid; seen.add(oid)
        relation = item["relation"]
        if relation not in {"ORIGIN", "REPEAT", "RELATED"}:
            raise DevelopmentFailurePatternError(f"{item_label}.relation is unsupported")
        positive_int(item["pr"], f"{label}.pr")
        sha40(item["head_sha"], f"{item_label}.head_sha")
        locator = nonempty(item["evidence_locator"], f"{label}.evidence_locator")
        if not LOCATOR_RE.fullmatch(locator):
            raise DevelopmentFailurePatternError(f"{item_label}.evidence_locator is invalid")
        reason = item["prevention_failure_reason"]
        if relation == "REPEAT":
            if reason not in REPEAT_FAILURE_REASONS:
                raise DevelopmentFailurePatternError(f"{item_label}.REPEAT requires a prevention_failure_reason")
        elif reason is not None:
            raise DevelopmentFailurePatternError(f"{item_label}.{relation} requires prevention_failure_reason=null")
        if relation == "ORIGIN":
            origin_count += 1
            if any(item[k] != origin[k] for k in ("pr", "head_sha", "evidence_locator")):
                raise DevelopmentFailurePatternError(f"{item_label}.ORIGIN must exactly match the pattern origin")
        result.append(item)
    if result[0]["relation"] != "ORIGIN" or origin_count != 1:
        raise DevelopmentFailurePatternError(f"{label} must begin with exactly one ORIGIN occurrence")
    return result


def validate_pattern(value: Any, root: Path, label: str, *, tracked: set[str] | None=None) -> dict[str, Any]:
    tracked = tracked if tracked is not None else tracked_regular_files(root)
    pattern = exact_object(value, TOP_FIELDS, label)
    if pattern["schema_version"] != SCHEMA_VERSION:
        raise DevelopmentFailurePatternError(f"{label}.schema_version is unsupported")
    pid = nonempty(pattern["pattern_id"], f"{label}.pattern_id")
    if not PATTERN_ID_RE.fullmatch(pid):
        raise DevelopmentFailurePatternError(f"{label}.pattern_id is invalid")
    if pattern["status"] not in {"ACTIVE", "RETIRED"}:
        raise DevelopmentFailurePatternError(f"{label}.status is unsupported")
    nonempty(pattern["title"], f"{label}.title")
    fclass = nonempty(pattern["failure_class"], f"{label}.failure_class")
    if not FAILURE_CLASS_RE.fullmatch(fclass):
        raise DevelopmentFailurePatternError(f"{label}.failure_class is invalid")
    origin = validate_origin(pattern["origin"], f"{label}.origin")
    for field in ("root_cause", "failure_mechanism", "violated_invariant"):
        nonempty(pattern[field], f"{label}.{field}")
    unique_strings(pattern["trigger_conditions"], f"{label}.trigger_conditions")
    unique_strings(pattern["applicable_scope"], f"{label}.applicable_scope")
    unique_strings(pattern["non_applicable_scope"], f"{label}.non_applicable_scope", allow_empty=True)
    search = validate_repository_search(pattern["repository_search"], root, f"{label}.repository_search", tracked)
    validate_prevention(pattern["prevention"], root, f"{label}.prevention", tracked)
    occurrences = validate_occurrences(pattern["occurrences"], pid, origin, f"{label}.occurrences")
    pending_unknown = [o for o in occurrences if o["relation"] == "REPEAT" and o["prevention_failure_reason"] == "UNKNOWN_PENDING_ANALYSIS"]
    if pending_unknown and search["status"] != "BOUNDED_FOLLOW_UP":
        raise DevelopmentFailurePatternError(f"{label} UNKNOWN_PENDING_ANALYSIS requires BOUNDED_FOLLOW_UP")
    if pattern["status"] == "RETIRED" and (search["status"] == "BOUNDED_FOLLOW_UP" or pending_unknown):
        raise DevelopmentFailurePatternError(
            f"{label} RETIRED pattern cannot hide unresolved follow-up or pending repeat analysis"
        )
    return pattern


def validate_schema_identity(root: Path) -> None:
    path = root / "data/schemas/development-failure-pattern-v1.schema.json"
    if not path.is_file():
        raise DevelopmentFailurePatternError(f"missing schema file: {path}")
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("properties",{}).get("schema_version",{}).get("const") != SCHEMA_VERSION:
        raise DevelopmentFailurePatternError("validator/schema DEVELOPMENT_FAILURE_PATTERN_V1 identity drift")


def load_registry(path: Path, root: Path) -> list[dict[str, Any]]:
    if not path.is_file():
        raise DevelopmentFailurePatternError(f"missing registry: {path}")
    tracked = tracked_regular_files(root); patterns=[]; ids=set(); classes=set(); previous=None
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            raw=json.loads(line)
        except json.JSONDecodeError as exc:
            raise DevelopmentFailurePatternError(f"{path}:{line_number}: invalid JSON: {exc.msg}") from exc
        pattern=validate_pattern(raw, root, f"{path}:{line_number}", tracked=tracked)
        pid=pattern["pattern_id"]; fclass=pattern["failure_class"]
        if pid in ids:
            raise DevelopmentFailurePatternError(f"duplicate pattern_id {pid}")
        if fclass in classes:
            raise DevelopmentFailurePatternError(f"duplicate failure_class {fclass}; use occurrences for repeats")
        if previous is not None and pid <= previous:
            raise DevelopmentFailurePatternError("registry must be ordered by pattern_id")
        previous=pid; ids.add(pid); classes.add(fclass); patterns.append(pattern)
    if not patterns:
        raise DevelopmentFailurePatternError("development failure-pattern registry must not be empty")
    return patterns


def active_summary(pattern: dict[str, Any]) -> dict[str, Any]:
    pending=[o["occurrence_id"] for o in pattern["occurrences"] if o["relation"]=="REPEAT" and o["prevention_failure_reason"]=="UNKNOWN_PENDING_ANALYSIS"]
    return {"pattern_id":pattern["pattern_id"],"failure_class":pattern["failure_class"],"title":pattern["title"],"trigger_conditions":pattern["trigger_conditions"],"applicable_scope":pattern["applicable_scope"],"search_status":pattern["repository_search"]["status"],"follow_up_refs":pattern["repository_search"]["follow_up_refs"],"pending_repeat_analysis":pending,"guard_refs":pattern["prevention"]["guard_refs"],"regression_refs":pattern["prevention"]["regression_refs"]}


def main() -> int:
    parser=argparse.ArgumentParser(description="Validate MimiSeek self-development repeat-prevention patterns")
    parser.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]); parser.add_argument("--registry",type=Path,default=Path("data/development-failure-patterns.jsonl")); parser.add_argument("--list-active",action="store_true")
    args=parser.parse_args(); root=args.root.resolve(); registry=args.registry if args.registry.is_absolute() else root/args.registry
    try:
        validate_schema_identity(root); patterns=load_registry(registry, root)
    except (DevelopmentFailurePatternError,OSError,json.JSONDecodeError) as exc:
        print(f"development failure-pattern validation failed: {exc}"); return 1
    if args.list_active:
        for pattern in patterns:
            if pattern["status"]=="ACTIVE":
                print(json.dumps(active_summary(pattern),ensure_ascii=False,sort_keys=True))
    else:
        print(f"development failure-pattern registry valid: patterns={len(patterns)} active={sum(p['status']=='ACTIVE' for p in patterns)}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
