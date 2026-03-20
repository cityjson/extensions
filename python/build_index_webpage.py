#!/usr/bin/env python3
"""Generate index.html for https://cityjson.github.io/extensions/.

Scans every subdirectory of extensions/, picks the latest version folder,
reads extension.toml, and writes a styled HTML overview page.
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
DEFAULT_OUT = ROOT / "_site" / "index.html"

BASE_URL = "https://cityjson.github.io/extensions"
GITHUB_URL = "https://github.com/cityjson/extensions/tree/main/extensions"


def parse_version(v: str) -> tuple:
    try:
        return tuple(int(x) for x in v.split("."))
    except ValueError:
        return (0,)


def strip_markdown_link(author: str) -> str:
    """Convert '[Name](url)' or 'Name <url>' to plain 'Name'."""
    author = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", author)
    author = re.sub(r"\s*<[^>]+>", "", author)
    return author.strip()


def latest_version(ext_dir: Path) -> str | None:
    versions = [d.name for d in ext_dir.iterdir() if d.is_dir()]
    if not versions:
        return None
    return max(versions, key=parse_version)


def collect_extensions() -> list[dict]:
    extensions = []
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
        extensions.append({
            "name": name,
            "version": version,
            "description": data.get("description", ""),
            "authors": [strip_markdown_link(a) for a in data.get("authors", [])],
        })
    return extensions


def render_row(ext: dict) -> str:
    name, version = ext["name"], ext["version"]
    description = ext["description"]
    authors = ", ".join(ext["authors"])
    github = f"{GITHUB_URL}/{name}/{version}"
    schema_url = f"{BASE_URL}/{name}/{version}/{name}.ext.json"
    schema_rel = f"{name}/{version}/{name}.ext.json"
    return (
        f"      <tr>\n"
        f"        <td><a class=\"ext-name\" href=\"{github}\">{name}</a></td>\n"
        f"        <td>{description}</td>\n"
        f"        <td>{version}</td>\n"
        f"        <td><a class=\"schema-link\" href=\"{schema_rel}\" title=\"{schema_url}\">{name}.ext.json</a></td>\n"
        f"        <td>{authors}</td>\n"
        f"      </tr>"
    )


def render_html(extensions: list[dict]) -> str:
    rows = "\n".join(render_row(e) for e in extensions)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CityJSON Extensions Registry</title>
  <link rel="stylesheet" href="https://unpkg.com/@knadh/oat/oat.min.css">
  <style>
    :root {{
      --primary: light-dark(#6449d6, #a08eff);
      --primary-foreground: light-dark(#fff, #09090b);
      --ring: light-dark(#6449d6, #a08eff);
      --accent: light-dark(#f0edfc, #1e1a2e);
      --accent-foreground: light-dark(#6449d6, #a08eff);
    }}

    body {{
      max-width: 960px;
      margin: 0 auto;
      padding: 2.5rem 1.5rem 4rem;
    }}

    header {{
      display: flex;
      align-items: center;
      gap: 1rem;
      margin-bottom: 2rem;
    }}

    header img {{
      height: 2.5rem;
    }}

    header h1 {{
      margin: 0;
      font-size: 1.6rem;
      font-weight: 600;
    }}

    .subtitle {{
      color: var(--muted-foreground);
      margin-top: -1.25rem;
      margin-bottom: 2rem;
      font-size: .95rem;
    }}

    table {{
      width: 100%;
    }}

    .ext-name {{
      font-weight: 600;
      color: var(--primary);
      text-decoration: none;
    }}

    .ext-name:hover {{
      text-decoration: underline;
    }}

    .schema-link {{
      font-family: var(--font-mono);
      font-size: .8rem;
    }}

    footer {{
      margin-top: 3rem;
      font-size: .85rem;
      color: var(--muted-foreground);
      border-top: 1px solid var(--border);
      padding-top: 1.25rem;
    }}

    footer a {{
      color: var(--muted-foreground);
    }}
  </style>
</head>
<body>

  <header>
    <img src="https://www.cityjson.org/assets/images/cityjson_logo.svg" alt="CityJSON logo">
    <h1>Extensions Registry</h1>
  </header>

  <p class="subtitle">
    Official registry of <a href="https://www.cityjson.org/extensions/">CityJSON Extensions</a>.
    Reference an extension in your CityJSON file using its schema URL below.
  </p>

  <table>
    <thead>
      <tr>
        <th>Extension</th>
        <th>Description</th>
        <th>Latest version</th>
        <th>Schema</th>
        <th>Developer(s)</th>
      </tr>
    </thead>
    <tbody>
{rows}
    </tbody>
  </table>

  <footer>
    <a href="https://www.cityjson.org/">cityjson.org</a> &middot;
    <a href="https://github.com/cityjson/extensions">GitHub</a> &middot;
    Each extension is licensed under its own terms.
  </footer>

</body>
</html>
"""


def main() -> None:
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_OUT
    extensions = collect_extensions()
    html = render_html(extensions)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    print(f"index.html written to {out} ({len(extensions)} extensions).")


if __name__ == "__main__":
    main()
