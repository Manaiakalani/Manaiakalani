#!/usr/bin/env python3
"""Generate Currently Building SVG cards and refresh the README section.

Selects the most recently pushed public, non-fork, non-archived repos and
writes dark/light SVG cards plus the README block between
CURRENTLY_BUILDING markers.
"""

from __future__ import annotations

import html
import json
import os
import re
import subprocess
import sys
import textwrap
from datetime import datetime, timezone
from pathlib import Path

from fonts import font_face_css

MAX_CARDS = 6
DIST_DIR = Path(os.environ.get("DIST_DIR", "dist"))
README_PATH = Path(os.environ.get("README_PATH", "README.md"))

# Extra repo names to hide from the grid (lowercase). CxE* and this profile
# repo are always excluded; archived / private / forks are too.
SKIP_REPOS = {
    # "manaiakalani.github.io",
}

LANG_COLORS = {
    "TypeScript": "#3178c6",
    "JavaScript": "#f1e05a",
    "Python": "#3572A5",
    "HTML": "#e34c26",
    "CSS": "#563d7c",
    "C++": "#f34b7d",
    "C": "#555555",
    "Go": "#00ADD8",
    "MDX": "#fcb32c",
    "Shell": "#89e051",
    "Java": "#b07219",
    "Ruby": "#701516",
    "Swift": "#F05138",
    "Rust": "#dea584",
    "C#": "#178600",
    "PHP": "#4F5D95",
    "Kotlin": "#A97BFF",
    "Dart": "#00B4AB",
    "Vue": "#41b883",
    "Svelte": "#ff3e00",
}

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "border": "#30363d",
        "title": "#58a6ff",
        "desc": "#8b949e",
        "meta": "#8b949e",
        "rule": "#21262d",
        "accent_a": "#1f6feb",
        "accent_b": "#a371f7",
        "dots": "#58a6ff",
    },
    "light": {
        "bg": "#ffffff",
        "border": "#d0d7de",
        "title": "#0969da",
        "desc": "#656d76",
        "meta": "#656d76",
        "rule": "#d0d7de",
        "accent_a": "#0969da",
        "accent_b": "#8250df",
        "dots": "#0969da",
    },
}

CARD_FONT_CSS = font_face_css("grotesk", "mono")
MONO = "Space Mono, ui-monospace, monospace"
GROTESK = "Space Grotesk, DM Sans, sans-serif"

SECTION_RE = re.compile(
    r"<!-- CURRENTLY_BUILDING:START -->.*?<!-- CURRENTLY_BUILDING:END -->",
    re.DOTALL,
)


def require_owner() -> str:
    owner = os.environ.get("OWNER") or os.environ.get("GITHUB_REPOSITORY_OWNER")
    if not owner:
        sys.exit("OWNER or GITHUB_REPOSITORY_OWNER is required")
    return owner


def fetch_repos(owner: str) -> list[dict]:
    endpoint = (
        f"users/{owner}/repos?sort=pushed&direction=desc&per_page=100&type=owner"
    )
    result = subprocess.run(
        ["gh", "api", "--paginate", endpoint],
        capture_output=True,
        text=True,
        check=False,
    )
    if result.returncode != 0:
        sys.exit(f"gh api failed:\n{result.stderr or result.stdout}")
    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        sys.exit(f"invalid JSON from gh api: {exc}")
    if not isinstance(data, list):
        sys.exit(f"unexpected API payload: {data!r:.200}")
    return data


def is_featured(repo: dict, owner: str) -> bool:
    name = (repo.get("name") or "").lower()
    if not name:
        return False
    if repo.get("fork") or repo.get("private") or repo.get("archived"):
        return False
    if name == owner.lower() or name.startswith("cxe"):
        return False
    if name in SKIP_REPOS:
        return False
    return True


def humanize_pushed(iso_str: str) -> str:
    if not iso_str:
        return ""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
    except ValueError:
        return ""
    delta = datetime.now(timezone.utc) - dt
    seconds = int(delta.total_seconds())
    if seconds < 0:
        return "just now"
    if seconds < 60:
        return "just now"
    if seconds < 3600:
        return f"{seconds // 60}m ago"
    if seconds < 86400:
        return f"{seconds // 3600}h ago"
    if seconds < 86400 * 30:
        return f"{seconds // 86400}d ago"
    if seconds < 86400 * 365:
        return f"{seconds // (86400 * 30)}mo ago"
    return f"{seconds // (86400 * 365)}y ago"


def ellipsize(text: str, max_chars: int) -> str:
    text = " ".join(text.split())
    if len(text) <= max_chars:
        return text
    return text[: max_chars - 3].rstrip() + "..."


def format_count(n: int) -> str:
    if n >= 1_000_000:
        return f"{n / 1_000_000:.1f}m".replace(".0m", "m")
    if n >= 1_000:
        return f"{n / 1_000:.1f}k".replace(".0k", "k")
    return str(n)


def wrap_description(desc: str, width: int = 48, max_lines: int = 2) -> list[str]:
    desc = " ".join((desc or "").split()) or "No description"
    lines = textwrap.wrap(desc, width=width, break_on_hyphens=False) or ["No description"]
    if len(lines) > max_lines:
        lines = lines[:max_lines]
        last = lines[-1].rstrip(".,;: ")
        if not last.endswith("..."):
            last = ellipsize(last + " ...", width)
        lines[-1] = last
    return lines


def generate_card(repo: dict, theme_name: str, idx: int) -> str:
    t = THEMES[theme_name]
    raw_name = ellipsize(repo["name"], 34)
    name = html.escape(raw_name, quote=False)
    aria = html.escape(raw_name, quote=True)
    desc_lines = [
        html.escape(line, quote=False)
        for line in wrap_description(repo.get("description") or "", width=48)
    ]
    lang_raw = repo.get("language") or ""
    lang = html.escape(lang_raw.upper() if lang_raw else "CODE", quote=False)
    stars = format_count(int(repo.get("stargazers_count") or 0))
    forks = format_count(int(repo.get("forks_count") or 0))
    updated = html.escape(humanize_pushed(repo.get("pushed_at") or "").upper(), quote=False)
    lang_color = LANG_COLORS.get(lang_raw, t["meta"])

    desc_svg = "\n".join(
        f'  <text fill="{t["desc"]}" font-family="{GROTESK}" font-size="13" font-weight="400" x="20" y="{76 + i * 18}">{line}</text>'
        for i, line in enumerate(desc_lines)
    )

    rule_y = 76 + len(desc_lines) * 18 + 14
    meta_y = rule_y + 22
    height = meta_y + 18
    pid = f"dots_{theme_name}_{idx}"
    gid = f"accent_{theme_name}_{idx}"
    clip = f"clip_{theme_name}_{idx}"

    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="400" height="{height}" role="img" aria-label="{aria}">
  <defs>
    <clipPath id="{clip}"><rect width="400" height="{height}" rx="12"/></clipPath>
    <linearGradient id="{gid}" x1="0%" x2="100%">
      <stop offset="0%" stop-color="{t["accent_a"]}">
        <animate attributeName="stop-color" values="{t["accent_a"]};{t["accent_b"]};{t["accent_a"]}" dur="6s" repeatCount="indefinite"/>
      </stop>
      <stop offset="100%" stop-color="{t["accent_b"]}">
        <animate attributeName="stop-color" values="{t["accent_b"]};{t["accent_a"]};{t["accent_b"]}" dur="6s" repeatCount="indefinite"/>
      </stop>
    </linearGradient>
    <pattern id="{pid}" width="16" height="16" patternUnits="userSpaceOnUse">
      <circle cx="1" cy="1" r="0.7" fill="{t["dots"]}"/>
    </pattern>
  </defs>
  <style>
{CARD_FONT_CSS}
  </style>
  <g clip-path="url(#{clip})">
  <rect width="400" height="{height}" rx="12" fill="{t["bg"]}"/>
  <rect width="400" height="{height}" rx="12" fill="url(#{pid})" opacity="0.12"/>
  <rect width="400" height="3" fill="url(#{gid})"/>
  </g>
  <rect width="400" height="{height}" rx="12" fill="none" stroke="{t["border"]}" stroke-width="1"/>
  <rect x="20" y="24" width="6" height="6" fill="{lang_color}"/>
  <text fill="{t["meta"]}" font-family="{MONO}" font-size="11" font-weight="400" letter-spacing="0.88" x="32" y="31">{lang}</text>
  <text fill="{t["meta"]}" font-family="{MONO}" font-size="11" font-weight="400" letter-spacing="0.88" x="380" y="31" text-anchor="end">{updated}</text>
  <text fill="{t["title"]}" font-family="{GROTESK}" font-size="16" font-weight="400" x="20" y="56">{name}</text>
{desc_svg}
  <line x1="20" y1="{rule_y}" x2="380" y2="{rule_y}" stroke="{t["rule"]}" stroke-width="1"/>
  <text fill="{t["meta"]}" font-family="{MONO}" font-size="11" font-weight="400" letter-spacing="0.88" x="20" y="{meta_y}">{stars} STARS</text>
  <text fill="{t["meta"]}" font-family="{MONO}" font-size="11" font-weight="400" letter-spacing="0.88" x="140" y="{meta_y}">{forks} FORKS</text>
</svg>
'''


def safe_filename(name: str) -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]", "-", name).strip(".-")
    return cleaned or "repo"


def write_cards(repos: list[dict]) -> None:
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    for path in DIST_DIR.glob("*.svg"):
        path.unlink()
    for idx, repo in enumerate(repos):
        filename = safe_filename(repo["name"])
        for theme in ("dark", "light"):
            (DIST_DIR / f"{filename}-{theme}.svg").write_text(
                generate_card(repo, theme, idx), encoding="utf-8"
            )
        print(f"  generated cards for {repo['name']}")


def render_readme_section(repos: list[dict], owner: str) -> str:
    owner_lower = owner.lower()
    lines = [
        "<!-- CURRENTLY_BUILDING:START -->",
        "<!-- generated by .github/scripts/update_currently_building.py; do not edit -->",
        '<div align="center">',
        "",
    ]
    for i, repo in enumerate(repos):
        name = repo["name"]
        filename = safe_filename(name)
        base = f"https://raw.githubusercontent.com/{owner_lower}/{owner_lower}/projects/{filename}"
        lines.append(f'<a href="https://github.com/{owner}/{name}">')
        lines.append("  <picture>")
        lines.append(f'    <source media="(prefers-color-scheme: dark)" srcset="{base}-dark.svg" />')
        lines.append(f'    <source media="(prefers-color-scheme: light)" srcset="{base}-light.svg" />')
        lines.append(f'    <img src="{base}-dark.svg" alt="{html.escape(name, quote=True)}" />')
        lines.append("  </picture>")
        if i % 2 == 0:
            lines.append("</a>&nbsp;")
        else:
            lines.append("</a>")
            if i < len(repos) - 1:
                lines.append("<br/>")
    lines.extend(["", "</div>", "<!-- CURRENTLY_BUILDING:END -->"])
    return "\n".join(lines)


def update_readme(section: str) -> None:
    content = README_PATH.read_text(encoding="utf-8")
    if not SECTION_RE.search(content):
        sys.exit("CURRENTLY_BUILDING markers not found in README.md")
    README_PATH.write_text(SECTION_RE.sub(section, content), encoding="utf-8")


def main() -> None:
    owner = require_owner()
    featured = [repo for repo in fetch_repos(owner) if is_featured(repo, owner)][:MAX_CARDS]
    if not featured:
        sys.exit("no public repos to feature; leaving README unchanged")
    write_cards(featured)
    update_readme(render_readme_section(featured, owner))
    names = [repo["name"] for repo in featured]
    print(f"Updated README with {len(featured)} repos: {names}")


if __name__ == "__main__":
    main()
