#!/usr/bin/env python3
"""Update the Available Extensions table in README.md.

Scans every subdirectory of extensions/, picks the latest version folder,
reads extension.toml, and rewrites the table between the marker comments in
README.md.
"""

import re
import sys
from pathlib import Path

try:
    import tomllib
except ImportError:
    sys.exit("Python 3.11+ is required (tomllib is a standard-library module).")

ROOT = Path(__file__).parent.parent
EXTENSIONS_DIR = ROOT / "extensions"
README = ROOT / "README.md"

TABLE_START = "<!-- EXTENSIONS_TABLE_START -->"
TABLE_END = "<!-- EXTENSIONS_TABLE_END -->"


def parse_version(v: str) -> tuple:
    """Convert a semver string to a comparable tuple of ints."""
    try:
        return tuple(int(x) for x in v.split("."))
    except ValueError:
        return (0,)


def strip_url(author: str) -> str:
    """Remove the optional URL in angle brackets from an author string.

    e.g. 'Hugo Ledoux <https://example.com>' -> 'Hugo Ledoux'
    """
    return re.sub(r"\s*<[^>]+>", "", author).strip()


def latest_version(ext_dir: Path) -> str | None:
    """Return the name of the latest version subdirectory, or None."""
    versions = [d.name for d in ext_dir.iterdir() if d.is_dir()]
    if not versions:
        return None
    return max(versions, key=parse_version)


def build_table() -> str:
    """Build a Markdown table for all extensions."""
    header = "| Extension | Description | Latest version | Developer(s) |"
    separator = "|-----------|-------------|----------------|--------------|"
    rows = [header, separator]

    for ext_dir in sorted(EXTENSIONS_DIR.iterdir()):
        if not ext_dir.is_dir():
            continue

        name = ext_dir.name
        version = latest_version(ext_dir)
        if version is None:
            continue

        toml_path = ext_dir / version / "extension.toml"
        if not toml_path.exists():
            print(f"  Warning: {toml_path} not found, skipping.", file=sys.stderr)
            continue

        with open(toml_path, "rb") as f:
            data = tomllib.load(f).get("extension", {})

        description = data.get("description", "")
        authors = data.get("authors", [])
        developers = ", ".join(strip_url(a) for a in authors)

        url = (
            f"https://cityjson.github.io/extensions/"
            f"{name}/{version}/{name}.ext.json"
        )
        rows.append(f"| [{name}]({url}) | {description} | {version} | {developers} |")

    return "\n".join(rows)


def update_readme() -> None:
    content = README.read_text(encoding="utf-8")
    table = build_table()
    new_block = f"{TABLE_START}\n{table}\n{TABLE_END}"

    if TABLE_START in content and TABLE_END in content:
        pattern = re.escape(TABLE_START) + r".*?" + re.escape(TABLE_END)
        new_content = re.sub(pattern, new_block, content, flags=re.DOTALL)
    else:
        # First run: insert after the "## Available Extensions" heading
        marker = "## Available Extensions\n"
        if marker not in content:
            sys.exit("Could not find '## Available Extensions' heading in README.md")
        new_content = content.replace(marker, f"{marker}\n{new_block}\n")

    README.write_text(new_content, encoding="utf-8")
    print("README.md updated successfully.")


if __name__ == "__main__":
    update_readme()
