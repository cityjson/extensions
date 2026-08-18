#!/usr/bin/env python3
"""Merge a val3dity JSON report into a CityJSON or CityJSONSeq file.

The script adds the Val3dity CityJSON Extension reference, stores the run
metadata in +val3dity-report, and attaches per-geometry diagnostics as
+val3dity-validation attributes on the CityObjects referenced by val3dity's
error ids.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


EXTENSION_URL = "https://cityjson.github.io/extensions/val3dity/0.2.0/val3dity.ext.json"
EXTENSION_VERSION = "0.2.0"
VALIDATION_ATTRIBUTE = "+val3dity-validation"
REPORT_PROPERTY = "+val3dity-report"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Merge a val3dity report into a CityJSON or CityJSONSeq file."
    )
    parser.add_argument("report", type=Path, help="Input val3dity report JSON file")
    parser.add_argument("cityjson", type=Path, help="Input CityJSON or CityJSONSeq file")
    parser.add_argument(
        "output",
        type=Path,
        nargs="?",
        help="Output CityJSON or CityJSONSeq file. Omit only with --in-place.",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite the input CityJSON file.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Allow overwriting an existing output file.",
    )
    parser.add_argument(
        "--include-valid",
        action="store_true",
        help="Also attach validity=true attributes for valid val3dity features.",
    )
    parser.add_argument(
        "--compact",
        action="store_true",
        help="Write normal CityJSON as compact JSON instead of pretty JSON.",
    )
    parser.add_argument(
        "--extension-url",
        default=EXTENSION_URL,
        help=f"Val3dity extension URL to write. Default: {EXTENSION_URL}",
    )
    parser.add_argument(
        "--extension-version",
        default=EXTENSION_VERSION,
        help=f"Val3dity extension version to write. Default: {EXTENSION_VERSION}",
    )
    return parser.parse_args()


def load_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def load_cityjson(path: Path) -> tuple[bool, Any]:
    text = path.read_text(encoding="utf-8")
    try:
        return False, json.loads(text)
    except json.JSONDecodeError:
        objects = [json.loads(line) for line in text.splitlines() if line.strip()]
        if not objects:
            raise ValueError(f"{path} is empty")
        return True, objects


def write_cityjson(path: Path, is_seq: bool, data: Any, compact: bool) -> None:
    with path.open("w", encoding="utf-8") as f:
        if is_seq:
            for obj in data:
                json.dump(obj, f, separators=(",", ":"), ensure_ascii=False)
                f.write("\n")
        else:
            if compact:
                json.dump(data, f, separators=(",", ":"), ensure_ascii=False)
            else:
                json.dump(data, f, indent=2, ensure_ascii=False)
                f.write("\n")


def scalar_report_parameters(parameters: dict[str, Any]) -> dict[str, Any]:
    out = {}
    for key, value in parameters.items():
        if isinstance(value, bool | int | float | str):
            out[key] = value
    return out


def copy_if_present(out: dict[str, Any], source: dict[str, Any], target: str, source_key: str) -> None:
    if source_key in source:
        out[target] = source[source_key]


def convert_dataset_error(error: Any) -> dict[str, Any] | None:
    if isinstance(error, int):
        return {"code": error, "description": "UNKNOWN"}
    if not isinstance(error, dict):
        return None
    if "code" not in error:
        return None

    out = {
        "code": error["code"],
        "description": str(error.get("description", "UNKNOWN")),
    }
    info = error.get("info")
    if info:
        out["info"] = str(info)
    source_id = error.get("id") or error.get("sourceId") or error.get("source_id")
    if source_id:
        out["sourceId"] = str(source_id)
    return out


def error_code_summary(report: dict[str, Any]) -> list[dict[str, int]]:
    counts: Counter[int] = Counter()
    for feature in report.get("features", []):
        for error in feature.get("errors", []):
            code = error.get("code")
            if isinstance(code, int):
                counts[code] += 1
    return [{"code": code, "count": counts[code]} for code in sorted(counts)]


def convert_report(report: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    copy_if_present(out, report, "val3dityVersion", "val3dity_version")
    copy_if_present(out, report, "validity", "validity")
    if "parameters" in report and isinstance(report["parameters"], dict):
        out["parameters"] = scalar_report_parameters(report["parameters"])
    copy_if_present(out, report, "featuresOverview", "features_overview")
    copy_if_present(out, report, "primitivesOverview", "primitives_overview")
    out["errorCodeSummary"] = error_code_summary(report)
    dataset_errors = [
        converted
        for converted in (convert_dataset_error(e) for e in report.get("dataset_errors", []))
        if converted is not None
    ]
    out["datasetErrors"] = dataset_errors
    return out


def parse_source_id(
    source_id: str, fallback_city_object_id: str
) -> tuple[str, int, dict[str, Any]]:
    raw_parts = {}
    for part in source_id.split("|"):
        if "=" in part:
            key, value = part.split("=", 1)
            raw_parts[key] = value

    city_object_id = raw_parts.get("coid", fallback_city_object_id)
    geometry_index = parse_non_negative_int(raw_parts.get("geom"), 0)
    if geometry_index is None:
        geometry_index = 0
    location: dict[str, Any] = {}
    optional_ints = {
        "shell": "shellIndex",
        "face": "faceIndex",
        "ring": "ringIndex",
        "vertex": "vertexIndex",
    }
    for source_key, target_key in optional_ints.items():
        value = parse_non_negative_int(raw_parts.get(source_key), None)
        if value is not None:
            location[target_key] = value
    return city_object_id, geometry_index, location


def parse_non_negative_int(value: str | None, default: int | None) -> int | None:
    if value is None:
        return default
    try:
        parsed = int(value)
    except ValueError:
        return default
    return parsed if parsed >= 0 else default


def convert_error(
    error: dict[str, Any], fallback_city_object_id: str
) -> tuple[str, int, dict[str, Any]]:
    source_id = str(error.get("id") or error.get("sourceId") or error.get("source_id") or "")
    city_object_id, geometry_index, location = parse_source_id(
        source_id, fallback_city_object_id
    )
    out = {
        "code": error.get("code"),
        "description": str(error.get("description", "UNKNOWN")),
        "sourceId": source_id,
        "location": location,
    }
    info = error.get("info")
    if info:
        out["info"] = str(info)
    return city_object_id, geometry_index, out


def build_validations(report: dict[str, Any], include_valid: bool) -> dict[str, dict[str, Any]]:
    working: dict[str, dict[str, Any]] = {}

    for feature in report.get("features", []):
        feature_id = str(feature.get("id", ""))
        errors = feature.get("errors", [])
        if not errors:
            if include_valid and feature_id:
                working.setdefault(feature_id, {"validity": bool(feature.get("validity", True))})
            continue

        for error in errors:
            city_object_id, geometry_index, converted = convert_error(error, feature_id)
            record = working.setdefault(
                city_object_id,
                {
                    "validity": False,
                    "_geometries": defaultdict(lambda: {"errors": []}),
                },
            )
            record["validity"] = False
            record.setdefault(
                "_geometries",
                defaultdict(lambda: {"errors": []}),
            )
            geometry = record["_geometries"][geometry_index]
            geometry["errors"].append(converted)

    return finalize_validations(working)


def finalize_validations(working: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    finalized = {}
    for city_object_id, record in working.items():
        out = {key: value for key, value in record.items() if not key.startswith("_")}
        geometries = record.get("_geometries")
        if geometries:
            out["geometries"] = [
                {
                    "geometryIndex": geometry_index,
                    "errors": geometry["errors"],
                }
                for geometry_index, geometry in sorted(geometries.items())
            ]
        finalized[city_object_id] = out
    return finalized


def add_extension(root: dict[str, Any], extension_url: str, extension_version: str) -> None:
    extensions = root.setdefault("extensions", {})
    extensions["val3dity"] = {
        "url": extension_url,
        "version": extension_version,
    }


def add_report(root: dict[str, Any], report: dict[str, Any], extension_url: str, extension_version: str) -> None:
    add_extension(root, extension_url, extension_version)
    root[REPORT_PROPERTY] = convert_report(report)


def attach_to_cityobjects(
    cityobjects: dict[str, Any],
    pending: dict[str, dict[str, Any]],
    applied: set[str],
) -> None:
    for city_object_id, validation in pending.items():
        city_object = cityobjects.get(city_object_id)
        if city_object is None:
            continue
        attributes = city_object.setdefault("attributes", {})
        attributes[VALIDATION_ATTRIBUTE] = validation
        applied.add(city_object_id)


def merge_normal_cityjson(
    cityjson: dict[str, Any],
    report: dict[str, Any],
    validations: dict[str, dict[str, Any]],
    extension_url: str,
    extension_version: str,
) -> set[str]:
    add_report(cityjson, report, extension_url, extension_version)
    applied: set[str] = set()
    attach_to_cityobjects(cityjson.get("CityObjects", {}), validations, applied)
    return applied


def merge_cityjson_seq(
    objects: list[dict[str, Any]],
    report: dict[str, Any],
    validations: dict[str, dict[str, Any]],
    extension_url: str,
    extension_version: str,
) -> set[str]:
    add_report(objects[0], report, extension_url, extension_version)
    applied: set[str] = set()
    for obj in objects:
        attach_to_cityobjects(obj.get("CityObjects", {}), validations, applied)
    return applied


def output_path(args: argparse.Namespace) -> Path:
    if args.in_place:
        if args.output is not None:
            raise SystemExit("--in-place cannot be used with an explicit output path")
        return args.cityjson
    if args.output is None:
        raise SystemExit("output is required unless --in-place is used")
    return args.output


def ensure_can_write(path: Path, args: argparse.Namespace) -> None:
    if path == args.cityjson:
        return
    if path.exists() and not args.overwrite:
        raise SystemExit(f"{path} already exists; use --overwrite to replace it")


def main() -> None:
    args = parse_args()
    out_path = output_path(args)
    ensure_can_write(out_path, args)

    report = load_json(args.report)
    is_seq, cityjson = load_cityjson(args.cityjson)
    validations = build_validations(report, args.include_valid)

    if is_seq:
        applied = merge_cityjson_seq(
            cityjson, report, validations, args.extension_url, args.extension_version
        )
    else:
        applied = merge_normal_cityjson(
            cityjson, report, validations, args.extension_url, args.extension_version
        )

    write_cityjson(out_path, is_seq, cityjson, args.compact)

    missing = sorted(set(validations) - applied)
    print(f"Wrote {out_path}")
    print(f"Attached {len(applied)} val3dity validation attribute(s)")
    if missing:
        print(
            f"Warning: {len(missing)} reported CityObject id(s) were not found: "
            + ", ".join(missing[:10]),
            file=sys.stderr,
        )
        if len(missing) > 10:
            print("Warning: missing id list truncated", file=sys.stderr)


if __name__ == "__main__":
    main()
