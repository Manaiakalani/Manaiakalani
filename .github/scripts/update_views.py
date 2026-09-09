#!/usr/bin/env python3
"""Build a self-hosted profile views badge from GitHub traffic.

GitHub README images are static, so this cannot increment on every page load.
It seeds from the previous Komarev total, then adds GitHub repo traffic
(the profile README) going forward. State lives on the `views` branch.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from fonts import font_face_css

DIST_DIR = Path(os.environ.get("DIST_DIR", "dist-views"))
SEED = int(os.environ.get("VIEWS_SEED", "709"))
SEED_DATE = os.environ.get("VIEWS_SEED_DATE", "2026-09-08")
MONO_CSS = font_face_css("mono")
MONO = "Space Mono, ui-monospace, monospace"

THEMES = {
    "dark": {"label_bg": "#21262d", "count_bg": "#1f6feb", "label": "#c9d1d9", "count": "#ffffff"},
    "light": {"label_bg": "#57606a", "count_bg": "#0969da", "label": "#ffffff", "count": "#ffffff"},
}


def require_repo() -> tuple[str, str]:
    owner = os.environ.get("OWNER") or os.environ.get("GITHUB_REPOSITORY_OWNER")
    repo = os.environ.get("REPO")
    if not repo:
        full = os.environ.get("GITHUB_REPOSITORY", "")
        if "/" in full:
            repo = full.split("/", 1)[1]
    if not owner or not repo:
        sys.exit("OWNER and REPO (or GITHUB_REPOSITORY) are required")
    return owner, repo


def gh_api(path: str) -> tuple[int, str]:
    result = subprocess.run(
        ["gh", "api", path],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.returncode, result.stdout or result.stderr


def load_state(owner: str, repo: str) -> dict:
    code, body = gh_api(f"repos/{owner}/{repo}/contents/count.json?ref=views")
    if code != 0:
        return {"seed": SEED, "seed_date": SEED_DATE, "days": {}}
    try:
        payload = json.loads(body)
        raw = payload.get("content", "")
        import base64

        return json.loads(base64.b64decode(raw).decode("utf-8"))
    except (json.JSONDecodeError, KeyError, ValueError):
        return {"seed": SEED, "seed_date": SEED_DATE, "days": {}}


def fetch_traffic(owner: str, repo: str) -> dict:
    code, body = gh_api(f"repos/{owner}/{repo}/traffic/views")
    if code != 0:
        print(f"traffic API unavailable ({code}): {body[:300]}", file=sys.stderr)
        return {"count": 0, "uniques": 0, "views": []}
    try:
        data = json.loads(body)
    except json.JSONDecodeError:
        return {"count": 0, "uniques": 0, "views": []}
    return data if isinstance(data, dict) else {"count": 0, "uniques": 0, "views": []}


def merge_days(state: dict, traffic: dict) -> dict:
    days = dict(state.get("days") or {})
    for row in traffic.get("views") or []:
        stamp = (row.get("timestamp") or "")[:10]
        if not stamp:
            continue
        prev = days.get(stamp, {"count": 0, "uniques": 0})
        count = max(int(prev.get("count") or 0), int(row.get("count") or 0))
        uniques = max(int(prev.get("uniques") or 0), int(row.get("uniques") or 0))
        if count or uniques:
            days[stamp] = {"count": count, "uniques": uniques}
    seed = int(state.get("seed") or SEED)
    seed_date = state.get("seed_date") or SEED_DATE
    extra = sum(
        int(v.get("count") or 0)
        for day, v in days.items()
        if day > seed_date
    )
    return {
        "seed": seed,
        "seed_date": seed_date,
        "lifetime": seed + extra,
        "days": dict(sorted(days.items())),
        "updated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }


def format_count(n: int) -> str:
    return f"{n:,}"


def mono_width(text: str, size: float, tracking: float = 0.0) -> float:
    return len(text) * size * 0.6 + max(0, len(text) - 1) * tracking


def generate_badge(count: int, theme_name: str) -> str:
    t = THEMES[theme_name]
    label = "VIEWS"
    value = format_count(count)
    size = 11
    pad_x = 8
    height = 20
    label_w = pad_x * 2 + mono_width(label, size, 0.7)
    count_w = pad_x * 2 + mono_width(value, size, 0.0)
    width = label_w + count_w
    label_cx = label_w / 2
    count_cx = label_w + count_w / 2
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width:.1f}" height="{height}" role="img" aria-label="profile views {value}">
  <style>
{MONO_CSS}
  </style>
  <mask id="m"><rect width="{width:.1f}" height="{height}" rx="3" fill="#fff"/></mask>
  <g mask="url(#m)">
    <rect width="{label_w:.1f}" height="{height}" fill="{t["label_bg"]}"/>
    <rect x="{label_w:.1f}" width="{count_w:.1f}" height="{height}" fill="{t["count_bg"]}"/>
  </g>
  <text x="{label_cx:.1f}" y="14" text-anchor="middle" fill="{t["label"]}" font-family="{MONO}" font-size="{size}" font-weight="400" letter-spacing="0.7">{label}</text>
  <text x="{count_cx:.1f}" y="14" text-anchor="middle" fill="{t["count"]}" font-family="{MONO}" font-size="{size}" font-weight="400">{value}</text>
</svg>
'''


def main() -> None:
    owner, repo = require_repo()
    state = merge_days(load_state(owner, repo), fetch_traffic(owner, repo))
    DIST_DIR.mkdir(parents=True, exist_ok=True)
    (DIST_DIR / "count.json").write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    for theme in ("dark", "light"):
        (DIST_DIR / f"views-{theme}.svg").write_text(
            generate_badge(state["lifetime"], theme), encoding="utf-8"
        )
    print(f"views badge: {state['lifetime']} (seed {state['seed']})")


if __name__ == "__main__":
    main()
