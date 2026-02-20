#!/usr/bin/env python3
"""Validate all JSON files in every examples/ folder using cjval.

Scans extensions/ for all examples/ subdirectories, runs `cjval -q` on each
JSON file found, and reports the results.  Also checks that the `uri` field in
each *.ext.json matches the expected URL derived from its path, and that each
example data file references the correct URL for its extension.

Exits with a non-zero status if any file fails validation.
"""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
EXTENSIONS_DIR = ROOT / "extensions"
BASE_URL = "https://cityjson.github.io/extensions"


def find_example_files() -> list[Path]:
    """Return all JSON files found inside any examples/ subdirectory."""
    return sorted(EXTENSIONS_DIR.glob("**/examples/*.json"))


def find_ext_json_files() -> list[Path]:
    """Return all *.ext.json files under the extensions directory."""
    return sorted(EXTENSIONS_DIR.glob("**/*.ext.json"))


def expected_url(ext_json_path: Path) -> str:
    """Derive the expected URL for an ext.json file from its path.

    Path pattern: extensions/{ext-name}/{version}/{filename}.ext.json
    Expected URL: {BASE_URL}/{ext-name}/{version}/{filename}.ext.json
    """
    # parts relative to EXTENSIONS_DIR: (ext-name, version, filename.ext.json)
    parts = ext_json_path.relative_to(EXTENSIONS_DIR).parts
    return f"{BASE_URL}/{'/'.join(parts)}"


def validate_ext_json_url(path: Path) -> tuple[bool, str]:
    """Check that the uri/url field in an ext.json matches the expected URL.

    Returns (ok, message).
    """
    with open(path) as f:
        data = json.load(f)

    actual = data.get("uri") or data.get("url")
    if actual is None:
        return False, "missing 'uri'/'url' field"

    expected = expected_url(path)
    if actual != expected:
        return False, f"expected '{expected}', got '{actual}'"

    return True, ""


def validate_example_url(path: Path) -> tuple[bool, str]:
    """Check that each extension URL in an example data file matches the
    expected URL derived from the ext.json in the same version folder.

    Returns (ok, message).
    """
    with open(path) as f:
        data = json.load(f)

    extensions = data.get("extensions", {})
    if not extensions:
        return True, ""

    # The example lives at: extensions/{ext-name}/{version}/examples/{file}.json
    # The ext.json lives at: extensions/{ext-name}/{version}/*.ext.json
    version_dir = path.parent.parent  # extensions/{ext-name}/{version}/
    ext_json_files = list(version_dir.glob("*.ext.json"))

    if not ext_json_files:
        return False, f"no *.ext.json found in {version_dir.relative_to(ROOT)}"

    expected = expected_url(ext_json_files[0])
    errors = []
    for key, entry in extensions.items():
        actual = entry.get("url")
        if actual is None:
            errors.append(f"extensions['{key}'] missing 'url' field")
        elif actual != expected:
            errors.append(f"extensions['{key}']: expected '{expected}', got '{actual}'")

    if errors:
        return False, "; ".join(errors)
    return True, ""


def validate_cjval(path: Path) -> bool:
    """Run cjval -q on *path*.  Returns True if valid, False otherwise."""
    result = subprocess.run(
        [Path.home() / "projects/cjval/target/debug/cjval", "-q", str(path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    return result.returncode == 0 and "File is valid" in output


def main() -> None:
    passed = []
    failed = []

    # --- Validate ext.json URLs ---
    ext_files = find_ext_json_files()
    if ext_files:
        print("Checking ext.json URLs:")
        for f in ext_files:
            relative = f.relative_to(ROOT)
            ok, msg = validate_ext_json_url(f)
            status = "OK  " if ok else "FAIL"
            suffix = f" -- {msg}" if msg else ""
            print(f"  [{status}] {relative}{suffix}")
            (passed if ok else failed).append(relative)
        print()

    # --- Validate example files (cjval + URL check) ---
    example_files = find_example_files()
    if not example_files:
        sys.exit(f"No example JSON files found under {EXTENSIONS_DIR}")

    print("Checking example files (cjval + URL):")
    for f in example_files:
        relative = f.relative_to(ROOT)
        cjval_ok = validate_cjval(f)
        url_ok, url_msg = validate_example_url(f)
        ok = cjval_ok and url_ok
        status = "OK  " if ok else "FAIL"
        notes = []
        if not cjval_ok:
            notes.append("cjval failed")
        if not url_ok:
            notes.append(url_msg)
        suffix = f" -- {'; '.join(notes)}" if notes else ""
        print(f"  [{status}] {relative}{suffix}")
        (passed if ok else failed).append(relative)

    total = len(ext_files) + len(example_files)
    print(f"\n{len(passed)}/{total} files valid.")

    if failed:
        print("\nFailed files:")
        for f in failed:
            print(f"  {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
