"""Load subset woff2 files and emit SVG @font-face CSS."""

from __future__ import annotations

import base64
from pathlib import Path

FONT_DIR = Path(__file__).resolve().parents[2] / "assets" / "fonts"

_SPECS = {
    "doto": ("Doto", "doto.woff2", "700"),
    "grotesk": ("Space Grotesk", "space-grotesk.woff2", "300 700"),
    "mono": ("Space Mono", "space-mono.woff2", "400"),
}


def data_uri(filename: str) -> str:
    raw = (FONT_DIR / filename).read_bytes()
    return "data:font/woff2;base64," + base64.b64encode(raw).decode("ascii")


def font_face_css(*keys: str) -> str:
    blocks = []
    for key in keys:
        family, filename, weight = _SPECS[key]
        blocks.append(
            f"""@font-face {{
  font-family: "{family}";
  src: url("{data_uri(filename)}") format("woff2");
  font-weight: {weight};
  font-style: normal;
}}"""
        )
    return "\n".join(blocks)
