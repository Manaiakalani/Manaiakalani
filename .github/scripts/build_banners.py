#!/usr/bin/env python3
"""Build Nothing-styled header, footer, and divider SVGs with embedded fonts.

Writes dark and light variants of each asset so the README can use
<picture> + prefers-color-scheme, matching the project cards, stats, and
snake. Run from anywhere: `python3 .github/scripts/build_banners.py`.
"""

from __future__ import annotations

from pathlib import Path

from fonts import font_face_css

ASSETS = Path(__file__).resolve().parents[2] / "assets"

NAME = "Maximilian (Manaiakalani) Stein"
ROLE = "PRODUCT MANAGER  /  MICROSOFT"
LOCATION = "REDMOND, WA"
KICKER = "PROFILE"
FOOTER_TITLE = "Mahalo for stopping by"
FOOTER_SUB = "BUILT WITH ALOHA  /  REDMOND, WA"

MONO = "Space Mono, ui-monospace, monospace"
GROTESK = "Space Grotesk, DM Sans, sans-serif"
DOTO = "Doto, Space Mono, monospace"

THEMES = {
    "dark": {
        "bg": "#0d1117",
        "bg_mid": "#161b22",
        "blue": "#58a6ff",
        "blue_deep": "#1f6feb",
        "purple": "#a371f7",
        "green": "#2ea043",
        "border": "#30363d",
        "display": "#ffffff",
        "secondary": "#8b949e",
        "glow_opacity": ("0.55", "0.10"),
        "wave_min_opacity": 0.15,
    },
    "light": {
        "bg": "#ffffff",
        "bg_mid": "#f6f8fa",
        "blue": "#0969da",
        "blue_deep": "#54aeff",
        "purple": "#8250df",
        "green": "#2da44e",
        "border": "#d0d7de",
        "display": "#1f2328",
        "secondary": "#656d76",
        "glow_opacity": ("0.30", "0.06"),
        "wave_min_opacity": 0.25,
    },
}


def paint_gradient(t: dict, gid: str, glow_id: str, *, reverse: bool = False) -> str:
    x1, y1, x2, y2 = ("100%", "100%", "0%", "0%") if reverse else ("0%", "0%", "100%", "100%")
    cx, cy = ("15%", "65%") if reverse else ("85%", "35%")
    g0, g1 = t["glow_opacity"]
    return f'''  <linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">
    <stop offset="0%" stop-color="{t["bg"]}"/>
    <stop offset="55%" stop-color="{t["bg_mid"]}"/>
    <stop offset="100%" stop-color="{t["blue_deep"]}">
      <animate attributeName="stop-color" values="{t["blue_deep"]};{t["green"]};{t["purple"]};{t["blue_deep"]}" dur="18s" repeatCount="indefinite"/>
    </stop>
  </linearGradient>
  <radialGradient id="{glow_id}" cx="{cx}" cy="{cy}" r="55%">
    <stop offset="0%" stop-color="{t["blue"]}" stop-opacity="{g0}"/>
    <stop offset="60%" stop-color="{t["blue"]}" stop-opacity="{g1}"/>
    <stop offset="100%" stop-color="{t["blue"]}" stop-opacity="0"/>
  </radialGradient>'''


def header_svg(theme: str) -> str:
    t = THEMES[theme]
    w, h = 854, 200
    css = "\n".join(
        [
            font_face_css("doto", text=NAME),
            font_face_css("mono", text=KICKER + LOCATION + ROLE),
        ]
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{NAME} — Product Manager • Microsoft">
  <defs>
{paint_gradient(t, "hbg", "hglow")}
  </defs>
  <style>
{css}
  </style>
  <rect width="{w}" height="{h}" rx="16" fill="url(#hbg)"/>
  <rect width="{w}" height="{h}" rx="16" fill="url(#hglow)">
    <animate attributeName="opacity" values="0.85;1;0.85" dur="6s" repeatCount="indefinite"/>
  </rect>
  <rect width="{w}" height="{h}" rx="16" fill="none" stroke="{t["border"]}" stroke-width="1"/>
  <text x="48" y="42" fill="{t["blue"]}" font-family="{MONO}" font-size="11" font-weight="400" letter-spacing="0.88">{KICKER}</text>
  <text x="806" y="42" text-anchor="end" fill="{t["secondary"]}" font-family="{MONO}" font-size="11" font-weight="400" letter-spacing="0.88">{LOCATION}</text>
  <text x="48" y="118" fill="{t["display"]}" font-family="{DOTO}" font-size="40" font-weight="700" letter-spacing="-0.8">{NAME}</text>
  <text x="48" y="158" fill="{t["secondary"]}" font-family="{MONO}" font-size="12" font-weight="400" letter-spacing="0.96">{ROLE}</text>
</svg>
'''


def footer_svg(theme: str) -> str:
    t = THEMES[theme]
    w, h = 854, 140
    css = "\n".join(
        [
            font_face_css("grotesk", text=FOOTER_TITLE),
            font_face_css("mono", text=FOOTER_SUB),
        ]
    )
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="Mahalo — made with aloha in the PNW">
  <defs>
{paint_gradient(t, "fbg", "fglow", reverse=True)}
  </defs>
  <style>
{css}
  </style>
  <rect width="{w}" height="{h}" rx="16" fill="url(#fbg)"/>
  <rect width="{w}" height="{h}" rx="16" fill="url(#fglow)">
    <animate attributeName="opacity" values="0.85;1;0.85" dur="6s" repeatCount="indefinite"/>
  </rect>
  <rect width="{w}" height="{h}" rx="16" fill="none" stroke="{t["border"]}" stroke-width="1"/>
  <text x="48" y="80" fill="{t["display"]}" font-family="{GROTESK}" font-size="24" font-weight="400">{FOOTER_TITLE}</text>
  <text x="48" y="110" fill="{t["secondary"]}" font-family="{MONO}" font-size="11" font-weight="400" letter-spacing="0.88">{FOOTER_SUB}</text>
</svg>
'''


def wave_svg(theme: str) -> str:
    t = THEMES[theme]
    w, h = 854, 24
    n = 40
    gap = 2
    x0 = 40
    usable = w - 80
    seg = (usable - gap * (n - 1)) / n
    mid = n // 2
    palette = (t["blue_deep"], t["blue"], t["purple"], t["green"], t["blue"])
    rects = []
    x = x0
    for i in range(n):
        dist = abs(i - mid) / mid
        opacity = max(t["wave_min_opacity"], 1 - dist)
        fill = palette[i % len(palette)] if i == mid else t["blue"]
        rects.append(
            f'  <rect x="{x:.2f}" y="10" width="{seg:.2f}" height="4" fill="{fill}" opacity="{opacity:.2f}"/>'
        )
        x += seg + gap
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="divider">
{chr(10).join(rects)}
</svg>
'''


def main() -> None:
    written = []
    for theme in THEMES:
        suffix = "" if theme == "dark" else "-light"
        for stem, builder in (("header", header_svg), ("footer", footer_svg), ("wave", wave_svg)):
            path = ASSETS / f"{stem}{suffix}.svg"
            path.write_text(builder(theme), encoding="utf-8")
            written.append(f"{path.name} ({path.stat().st_size // 1024} KB)")
    print("wrote " + ", ".join(written))


if __name__ == "__main__":
    main()
