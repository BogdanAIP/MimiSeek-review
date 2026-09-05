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
ISSUE_FOLLOW_UP_RE = re.compile(
    r"^https://github\.com/BogdanAIP/MimiSeek-review/issues/[1-9][0-9]*$"
)
REGULAR_GIT_MODES = {"100644", "100755"}
REPEAT_FAILURE_REASONS = {
    "NO_GUARD",
    "GUARD_TOO_NARROW",
    "GUARD_NOT_IN_CI",
    "PATTERN_NOT_RETRIEVED",
    "SCOPE_WRONG",
    "NEW_VARIANT",
    "UNKNOWN_PENDING_ANALYSIS",
}

TOP_FIELDS = {
    "schema_version", "pattern_id", "status", "title", "failure_class", "origin",
    "root_cause", "failure_mechanism", "violated_invariant", "trigger_conditions",
    "applicable_scope", "non_applicable_scope", "repository_search", "prevention",
    "occurrences",
}
ORIGIN_FIELDS = {"source_kind", "repository", "pr", "head_sha", "evidence_locator"}
SEARCH_FIELDS = {"status", "searched_scope", "discovered_instances", "follow_up_refs", "notes"}
PREVENTION_FIELDS = {"kind", "guard_refs", "regression_refs", "manual_only_reason"}
OCCURRENCE_FIELDS = {
    "occurrence_id", "relation", "pr", "head_sha", "evidence_locator",
    "prevention_failure_reason",
}


class DevelopmentFailurePatternError(RuntimeError):
    pass


def exact_object(value: Any, fields: set[str], label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise DevelopmentFailurePatternError(f"{label} must be an object")
    if set(value) != fields:
        raise DevelopmentFailurePatternError(
            f"{label} shape mismatch; missing={sorted(fields-set(value))} "
            f"unknown={sorted(set(value)-fields)}"
        )
    return value


def nonempty(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise DevelopmentFailurePatternError(f"{label} must be a non-empty string")
    return value


def unique_strings(value: Any, label: str, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list) or any(not isinstance(x, str) or not x.strip() for x in value):
        raise DevelopmentFailurePatternError(f"{label} must be an array of non-empty strings")
    if not allow_empty and not value:
        raise DevelopmentFailurePatternError(f"{label} must not be empty")
    if len(value) != len(set(value)):
        raise DevelopmentFailurePatternError(f"{label} contains duplicates")
    return value


def positive_int(value: Any, label: str) -> int:
    if not isinstance(value, int) or isinstance(value, bool) or value < 1:
        raise DevelopmentFailurePatternError(f"{label} must be a positive integer")
    return value


def sha40(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SHA40_RE.fullmatch(value):
        raise DevelopmentFailurePatternError(f"{label} must be a lowercase 40-character SHA")
    return value


def repo_relative(value: str, label: str) -> str:
    raw = value.split("#", 1)[0]
    path = Path(raw)
    if path.is_absolute() or not path.parts or ".." in path.parts:
        raise DevelopmentFailurePatternError(f"{label} must be a repository-relative path")
    if path.parts[0] == ".git":
        raise DevelopmentFailurePatternError(f"{label} must not reference .git metadata")
    return path.as_posix()


def tracked_regular_files(root: Path) -> set[str]:
    root = root.resolve()
    try:
        top = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
        ).stdout.strip()
        if Path(top).resolve() != root:
            raise DevelopmentFailurePatternError(
                f"repeat-prevention root is not the Git toplevel: root={root} git={top}"
            )
        raw = subprocess.run(
            ["git", "-C", str(root), "ls-tree", "-r", "-z", "--full-tree", "HEAD"],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        ).stdout
    except DevelopmentFailurePatternError:
        raise
    except (OSError, subprocess.CalledProcessError) as exc:
        raise DevelopmentFailurePatternError(
            "repeat-prevention validation requires an exact Git HEAD tree"
        ) from exc

    result: set[str] = set()
    for record in raw.split(b"\0"):
        if not record:
            continue
        try:
            meta, path_bytes = record.split(b"\t", 1)
            mode, kind, _sha = meta.decode("ascii").split()
            path = path_bytes.decode("utf-8")
        except (ValueError, UnicodeDecodeError) as exc:
            raise DevelopmentFailurePatternError("malformed/non-UTF8 exact HEAD tree entry") from exc
        if mode in REGULAR_GIT_MODES and kind == "blob":
            result.add(path)
    return result


def tracked_ref(root: Path, value: str, label: str, tracked: set[str]) -> str:
    path = repo_relative(value, label)
    if path not in tracked:
        raise DevelopmentFailurePatternError(
            f"{label} is not a tracked regular file in exact HEAD: {path}"
        )
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
    if ISSUE_FOLLOW_UP_RE.fullmatch(ref):
        return ref
    if "://" in ref:
        raise DevelopmentFailurePatternError(
            f"{label} must be an exact MimiSeek issue URL or tracked regular file"
        )
    try:
        return tracked_ref(root, ref, label, tracked)
    except DevelopmentFailurePatternError as exc:
        raise DevelopmentFailurePatternError(
            f"{label} must be an exact MimiSeek issue URL or tracked regular file: {ref}"
        ) from exc


def validate_origin(value: Any, label: str) -> dict[str, Any]:
    origin = exact_object(value, ORIGIN_FIELDS, label)
    if origin["source_kind"] not in {"REVIEW_FINDING", "PROCESS_INCIDENT"}:
        raise DevelopmentFailurePatternError(f"{label}.source_kind is unsupported")
    if origin["repository"] != REPOSITORY:
        raise DevelopmentFailurePatternError(f"{label}.repository must remain scoped to {REPOSITORY}")
    positive_int(origin["pr"], f"{label}.pr")
    sha40(origin["head_sha"], f"{label}.head_sha")
    locator = nonempty(origin["evidence_locator"], f"{label}.evidence_locator")
    if not LOCATOR_RE.fullmatch(locator):
        raise DevelopmentFailurePatternError(f"{label}.evidence_locator is invalid")
    return origin


def validate_search(value: Any, root: Path, label: str, tracked: set[str]) -> dict[str, Any]:
    search = exact_object(value, SEARCH_FIELDS, label)
    if search["status"] not in {"COMPLETED", "BOUNDED_FOLLOW_UP"}:
        raise DevelopmentFailurePatternError(f"{label}.status is unsupported")
    scopes = unique_strings(search["searched_scope"], f"{label}.searched_scope")
    discovered = unique_strings(search["discovered_instances"], f"{label}.discovered_instances", allow_empty=True)
    followups = unique_strings(search["follow_up_refs"], f"{label}.follow_up_refs", allow_empty=True)
    nonempty(search["notes"], f"{label}.notes")
    if search["status"] == "COMPLETED" and followups:
        raise DevelopmentFailurePatternError(f"{label}.COMPLETED search must not retain follow_up_refs")
    if search["status"] == "BOUNDED_FOLLOW_UP" and not followups:
        raise DevelopmentFailurePatternError(f"{label}.BOUNDED_FOLLOW_UP requires at least one follow_up_ref")
    for i, pattern in enumerate(scopes, 1):
        normalized = repo_relative(pattern, f"{label}.searched_scope[{i}")
        if not any(fnmatch.fnmatchcase(path, normalized) for path in tracked):
            raise DevelopmentFailurePatternError(f"{label}.searched_scope[{i}] matches no tracked regular files in exact HEAD: {pattern}")
    for i, item in enumerate(discovered, 1):
        tracked_ref(root, item, f"{label}.discovered_instances[{i}]", tracked)
    for i, item in enumerate(followups, 1):
        follow_up_ref(root, item, f"{label}.follow_up_refs[{i}]", tracked)
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


def validate_pattern(
    value: Any, root: Path, label: str, *, tracked: set[str] | None = None
) -> dict[str, Any]:
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
    search = validate_search(pattern["repository_search"], root, f"{label}.repository_search", tracked)
    validate_prevention(pattern["prevention"], root, f"{label}.prevention", tracked)
    occurrences = validate_occurrences(pattern["occurrences"], pid, origin, f"{label}.occurrences")
    pending = [
        item["occurrence_id"] for item in occurrences
        if item["relation"] == "REPEAT"
        and itemVÈœ™]™[[Û—Ù˜Z[\™WÜ™X\ÛÛˆ—HOH•S’Ó“ÕÓ—ÔS‘S‘×ĞSSTÒTÈ‚ˆBˆYˆ[™[™È[™ÙX\˜ÚÈœİ]\È—HOH“ÕS‘QÑ“ÓÕ×ÕT‚ˆ˜Z\ÙH]™[ÜY[˜Z[\™T]\›‘\œ›ÜŠˆˆÛX™[K•S’Ó“ÕÓ—ÔS‘S‘×ĞSSTÒTÈ™\]Z\™\È“ÕS‘QÑ“ÓÕ×ÕTÚ]\˜X›H›ÛİË]\‚ˆ
Bˆ™]\›ˆ]\›‚‚‚™Yˆ˜[Y]WÜØÚ[XWÚY[]J›Ûİˆ]
HOˆ›Û™N‚ˆ]H›ÛİÈ™]KÜØÚ[X\ËÙ]™[ÜY[Y˜Z[\™K\]\›‹]ŒKœØÚ[XKšœÛÛˆ‚ˆYˆ›İ]š\×Ùš[J
N‚ˆ˜Z\ÙH]™[ÜY[˜Z[\™T]\›‘\œ›ÜŠˆ›Z\ÜÚ[™ÈØÚ[XHš[NˆÜ]HŠBˆ˜]ÈHœÛÛ‹›ØYÊ]œ™XYİ^
[˜ÛÙ[™ÏH]‹NŠJBˆN‚ˆ™\œÚ[ÛˆH˜]ÖÈœ›Ü\Y\È—VÈœØÚ[XWİ™\œÚ[Ûˆ—VÈ˜ÛÛœİ—Bˆ^Ù\
Ù^Q\œ›Ü‹\Q\œ›ÜŠH\È^Î‚ˆ˜Z\ÙH]™[ÜY[˜Z[\™T]\›‘\œ›ÜŠ™]™[ÜY[˜Z[\™K\]\›ˆØÚ[XHXÚÜÈØÚ[XWİ™\œÚ[ÛˆÛÛœİŠHœ›ÛH^ÂˆYˆ™\œÚ[ÛˆOHĞÒSPWÕ‘T”ÒSÓ‚ˆ˜Z\ÙH]™[ÜY[˜Z[\™T]\›‘\œ›ÜŠ˜[Y]Ü‹ÜØÚ[XHU‘SÔQS•ÑRST‘WÔUT“—ÕŒHY[]HšYŠB‚‚™YˆØYÜ™YÚ\İJ]ˆ]›Ûİˆ]
HOˆ\İÙXİÜİ‹[WWN‚ˆYˆ›İ]š\×Ùš[J
N‚ˆ˜Z\ÙH]™[ÜY[˜Z[\™T]\›‘\œ›ÜŠˆ›Z\ÜÚ[™È™YÚ\İNˆÜ]HŠBˆ˜XÚÙYH˜XÚÙYÜ™Yİ[\—Ùš[\Ê›Ûİ
Bˆ]\›œÎˆ\İÙXİÜİ‹[WWHH×BˆÙY[—ÚYÎˆÙ]Üİ—HHÙ]

BˆÙY[—ØÛ\ÜÙ\ÎˆÙ]Üİ—HHÙ]

Bˆ™]š[İ\Îˆİˆ›Û™HH›Û™Bˆ›Üˆ[™WÛ[X™\‹[™H[ˆ[[Y\˜]J]œ™XYİ^
[˜ÛÙ[™ÏH]‹NŠKœÜ][™\Ê
KJN‚ˆYˆ›İ[™Kœİš\

N‚ˆÛÛ[YBˆN‚ˆ˜]ÈHœÛÛ‹›ØYÊ[™JBˆ^Ù\œÛÛ‹’”ÓÓ‘XÛÙQ\œ›Üˆ\È^Î‚ˆ˜Z\ÙH]™[ÜY[˜Z[\™T]\›‘\œ›ÜŠˆÜ]NÛ[™WÛ[X™\ŸNˆ[˜[Y”ÓÓˆÙ^Ë›\ÙßHŠHœ›ÛH^Âˆ]\›ˆH˜[Y]WÜ]\›Š˜]Ë›ÛİˆÜ]NÛ[™WÛ[X™\ŸH‹˜XÚÙY]˜XÚÙY
BˆYH]\›–Èœ]\›—ÚY—Bˆ˜Û\ÜÈH]\›–È™˜Z[\™WØÛ\ÜÈ—BˆYˆY[ˆÙY[—ÚYÎ‚ˆ˜Z\ÙH]™[ÜY[˜Z[\™T]\›‘\œ›ÜŠˆ™\XØ]H]\›—ÚYÜYHŠBˆYˆ˜Û\ÜÈ[ˆÙY[—ØÛ\ÜÙ\Î‚ˆ˜Z\ÙH]™[ÜY[˜Z[\™T]\›‘\œ›ÜŠˆ™\XØ]H˜Z[\™WØÛ\ÜÈÙ˜Û\ÜßNÈ\ÙHØØİ\œ™[˜Ù\È›Üˆ™\X]ÈŠBˆYˆ™]š[İ\È\È›İ›Û™H[™YH™]š[İ\Î‚ˆ˜Z\ÙH]™[ÜY[˜Z[\™T]\›‘\œ›ÜŠœ™YÚ\İH]\İ™HÜ™\™YH]\›—ÚYŠBˆ™]š[İ\ÈHYÈÙY[—ÚYË˜Y
Y
NÈÙY[—ØÛ\ÜÙ\Ë˜Y
˜Û\ÜÊNÈ]\›œË˜\[™
]\›ŠBˆYˆ›İ]\›œÎ‚ˆ˜Z\ÙH]™[ÜY[˜Z[\™T]\›‘\œ›ÜŠ™]™[ÜY[˜Z[\™K\]\›ˆ™YÚ\İH]\İ›İ™H[\HŠBˆ™]\›ˆ]\›œÂ‚‚™YˆXİ]™WÜİ[[X\J]\›ˆXİÜİ‹[WJHOˆXİÜİ‹[WN‚ˆ[™[™ÈHÂˆ][VÈ›ØØİ\œ™[˜ÙWÚY—H›Üˆ][H[ˆ]\›–È›ØØİ\œ™[˜Ù\È—BˆYˆ][VÈœ™[][Ûˆ—HOH”‘TPU‚ˆ[™][VÈœ™]™[[Û—Ù˜Z[\™WÜ™X\ÛÛˆ—HOH•S’Ó“ÕÓ—ÔS‘S‘×ĞSSTÒTÈ‚ˆBˆ™]\›ˆÂˆœ]\›—ÚYˆ]\›–Èœ]\›—ÚY—Kˆ™˜Z[\™WØÛ\ÜÈˆ]\›–È™˜Z[\™WØÛ\ÜÈ—Kˆ]Hˆ]\›–È]H—KˆšYÙÙ\—ØÛÛ™][ÛœÈˆ]\›–ÈšYÙÙ\—ØÛÛ™][ÛœÈ—Kˆ˜\XØX›WÜØÛÜHˆ]\›–È˜\XØX›WÜØÛÜH—KˆœÙX\˜ÚÜİ]\Èˆ]\›–Èœ™\ÜÚ]ÜWÜÙX\˜Ú—VÈœİ]\È—Kˆ™›Ûİ×İ\Ü™YœÈˆ]\›–Èœ™\ÜÚ]ÜWÜÙX\˜Ú—VÈ™›Ûİ×İ\Ü™YœÈ—Kˆœ[™[™×Ü™\X]Ø[˜[\Ú\Èˆ[™[™Ëˆ™İX\™Ü™YœÈˆ]\›–Èœ™]™[[Ûˆ—VÈ™İX\™Ü™YœÈ—Kˆœ™YÜ™\ÜÚ[Û—Ü™YœÈˆ]\›–Èœ™]™[[Ûˆ—VÈœ™YÜ™\ÜÚ[Û—Ü™YœÈ—KˆB‚‚™YˆXZ[Š
HOˆ[‚ˆ\œÙ\ˆH\™Ü\œÙK\™İ[Y[\œÙ\Š\ØÜš\[ÛH•˜[Y]HZ[ZTÙYZÈÙ[‹Y]™[ÜY[™\X]\™]™[[Ûˆ]\›œÈŠBˆ\œÙ\‹˜YØ\™İ[Y[
‹K\›Ûİ‹\OT]Y˜][T]
×Ùš[W×ÊKœ™\ÛÛ™J
Kœ\™[ÖÌWJBˆ\œÙ\‹˜YØ\™İ[Y[
‹K\™YÚ\İH‹\OT]Y˜][T]
™]KÙ]™[ÜY[Y˜Z[\™K\]\›œËšœÛÛ›ŠJBˆ\œÙ\‹˜YØ\™İ[Y[
‹K[\İXXİ]™H‹Xİ[ÛHœİÜ™WİYHŠBˆ\™ÜÈH\œÙ\‹œ\œÙWØ\™ÜÊ
Bˆ›ÛİH\™ÜËœ›Ûİœ™\ÛÛ™J
Bˆ™YÚ\İHH\™ÜËœ™YÚ\İHYˆ\™ÜËœ™YÚ\İKš\×ØXœÛÛ]J
H[ÙH›ÛİÈ\™ÜËœ™YÚ\İBˆN‚ˆ˜[Y]WÜØÚ[XWÚY[]J›Ûİ
Bˆ]\›œÈHØYÜ™YÚ\İJ™YÚ\İK›Ûİ
Bˆ^Ù\
]™[ÜY[˜Z[\™T]\›‘\œ›Ü‹ÔÑ\œ›Ü‹œÛÛ‹’”ÓÓ‘XÛÙQ\œ›ÜŠH\È^Î‚ˆš[
ˆ™]™[ÜY[˜Z[\™K\]\›ˆ˜[Y][Ûˆ˜Z[YˆÙ^ßHŠBˆ™]\›ˆBˆYˆ\™ÜË›\İØXİ]™N‚ˆ›Üˆ]\›ˆ[ˆ]\›œÎ‚ˆYˆ]\›–Èœİ]\È—HOHPÕU‘H‚ˆš[
œÛÛ‹™[\ÊXİ]™WÜİ[[X\J]\›ŠK[œİ\™WØ\ØÚZOQ˜[ÙKÛÜÚÙ^\ÏUYJJBˆ[ÙN‚ˆXİ]™HHİ[J]\›–Èœİ]\È—HOHPÕU‘Hˆ›Üˆ]\›ˆ[ˆ]\›œÊBˆš[
ˆ™]™[ÜY[˜Z[\™K\]\›ˆ™YÚ\İH˜[Yˆ]\›œÏ^Û[Š]\›œÊ_HXİ]™O^ØXİ]™_HŠBˆ™]\›ˆ‚‚šYˆ×Û˜[YW×ÈOH—×ÛXZ[—×È‚ˆ˜Z\ÙHŞ\İ[Q^]
XZ[Š
JB