"""Load subset woff2 files and emit SVG @font-face CSS.

When ``text`` is supplied and fonttools + brotli are importable, each font is
re-subset to only the glyphs that text uses, which keeps per-card payloads to
a few KB instead of embedding the whole ~30 KB subset in every SVG. Without
those packages (or without ``text``) the pre-built subset is embedded as-is.
"""

from __future__ import annotations

import base64
import io
import sys
from functools import lru_cache
from pathlib import Path

FONT_DIR = Path(__file__).resolve().parents[2] / "assets" / "fonts"

_SPECS = {
    "doto": ("Doto", "doto.woff2", "700"),
    "grotesk": ("Space Grotesk", "space-grotesk.woff2", "300 700"),
    "mono": ("Space Mono", "space-mono.woff2", "400"),
}

try:  # optional dependency; see requirements.txt
    from fontTools import subset as _ft_subset
    from fontTools.ttLib import TTFont as _TTFont

    _CAN_SUBSET = True
except ImportError:  # pragma: no cover - exercised only without fonttools
    _CAN_SUBSET = False


@lru_cache(maxsize=None)
def _font_bytes(filename: str) -> bytes:
    return (FONT_DIR / filename).read_bytes()


def _subset_bytes(filename: str, text: str) -> bytes:
    """Return a woff2 containing only glyphs needed for ``text``."""
    if not _CAN_SUBSET or not text:
        return _font_bytes(filename)
    try:
        font = _TTFont(io.BytesIO(_font_bytes(filename)))
        options = _ft_subset.Options()
        options.flavor = "woff2"
        options.layout_features = ["kern", "liga", "calt"]
        options.hinting = False
        options.desubroutinize = True
        subsetter = _ft_subset.Subsetter(options=options)
        # Always keep space + the text itself; ensure fallback glyphs exist.
        subsetter.populate(text=text + " ")
        subsetter.subset(font)
        out = io.BytesIO()
        font.flavor = "woff2"
        font.save(out)
        data = out.getvalue()
        # If brotli is missing, fontTools raises; if the result is somehow
        # larger than the source, keep the source.
        return data if len(data) < len(_font_bytes(filename)) else _font_bytes(filename)
    except Exception as exc:  # noqa: BLE001 - never fail a build over fonts
        print(f"font subset failed for {filename}: {exc}", file=sys.stderr)
        return _font_bytes(filename)


def data_uri(filename: str, text: str | None = None) -> str:
    raw = _subset_bytes(filename, text or "")
    return "data:font/woff2;base64," + base64.b64encode(raw).decode("ascii")


def font_face_css(*keys: str, text: str | None = None) -> str:
    """Emit @font-face blocks for ``keys``.

    ``text`` is the full string content that will be rendered with these fonts;
    when given, fonts are subset to just those glyphs.
    """
    blocks = []
    for key in keys:
        family, filename, weight = _SPECS[key]
        blocks.append(
            f"""@font-face {{
  font-family: "{family}";
  src: url("{data_uri(filename, text)}") format("woff2");
  font-weight: {weight};
  font-style: normal;
}}"""
        )
    return "\n".join(blocks)
