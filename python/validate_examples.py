#!/usr/bin/env python3
"""Validate all JSON files in every examples/ folder using cjval.

Scans extensions/ for all examples/ subdirectories, runs `cjval -q` on each
JSON file found, and reports the results.  Exits with a non-zero status if any
file fails validation.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
EXTENSIONS_DIR = ROOT / "extensions"


def find_example_files() -> list[Path]:
    """Return all JSON files found inside any examples/ subdirectory."""
    return sorted(EXTENSIONS_DIR.glob("**/examples/*.json"))


def validate(path: Path) -> bool:
    """Run cjval -q on *path*.  Returns True if valid, False otherwise."""
    result = subprocess.run(
        [Path.home() / "projects/cjval/target/debug/cjval", "-q", str(path)],
        capture_output=True,
        text=True,
    )
    output = result.stdout + result.stderr
    return result.returncode == 0 and "File is valid" in output


def main() -> None:
    files = find_example_files()
    if not files:
        sys.exit(f"No example JSON files found under {EXTENSIONS_DIR}")

    passed = []
    failed = []

    for f in files:
        relative = f.relative_to(ROOT)
        ok = validate(f)
        status = "OK  " if ok else "FAIL"
        print(f"  [{status}] {relative}")
        (passed if ok else failed).append(relative)

    total = len(files)
    print(f"\n{len(passed)}/{total} files valid.")

    if failed:
        print("\nFailed files:")
        for f in failed:
            print(f"  {f}")
        sys.exit(1)


if __name__ == "__main__":
    main()
