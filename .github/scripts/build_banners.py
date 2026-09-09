#!/usr/bin/env python3
"""Build Nothing-styled header, footer, and divider SVGs with embedded fonts."""

from __future__ import annotations

from pathlib import Path

from fonts import font_face_css

ASSETS = Path(__file__).resolve().parents[2] / "assets"

BG = "#0d1117"
BG_MID = "#161b22"
BLUE = "#58a6ff"
BLUE_DEEP = "#1f6feb"
PURPLE = "#a371f7"
GREEN = "#2ea043"
BORDER = "#30363d"
TEXT_DISPLAY = "#FFFFFF"
TEXT_SECONDARY = "#8b949e"

BANNER_CSS = font_face_css("doto", "grotesk", "mono")


def paint_gradient(gid: str, glow_id: str, *, reverse: bool = False) -> str:
    x1, y1, x2, y2 = ("100%", "100%", "0%", "0%") if reverse else ("0%", "0%", "100%", "100%")
    cx, cy = ("15%", "65%") if reverse else ("85%", "35%")
    return f'''  <linearGradient id="{gid}" x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}">
    <stop offset="0%" stop-color="{BG}"/>
    <stop offset="55%" stop-color="{BG_MID}"/>
    <stop offset="100%" stop-color="{BLUE_DEEP}">
      <animate attributeName="stop-color" values="{BLUE_DEEP};{GREEN};{PURPLE};{BLUE_DEEP}" dur="18s" repeatCount="indefinite"/>
    </stop>
  </linearGradient>
  <radialGradient id="{glow_id}" cx="{cx}" cy="{cy}" r="55%">
    <stop offset="0%" stop-color="{BLUE}" stop-opacity="0.55"/>
    <stop offset="60%" stop-color="{BLUE}" stop-opacity="0.10"/>
    <stop offset="100%" stop-color="{BLUE}" stop-opacity="0"/>
  </radialGradient>'''


def header_svg() -> str:
    w, h = 854, 200
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="Maximilian (Manaiakalani) Stein — Product Manager • Microsoft">
  <defs>
{paint_gradient("hbg", "hglow")}
  </defs>
  <style>
{BANNER_CSS}
  </style>
  <rect width="{w}" height="{h}" rx="16" fill="url(#hbg)"/>
  <rect width="{w}" height="{h}" rx="16" fill="url(#hglow)">
    <animate attributeName="opacity" values="0.85;1;0.85" dur="6s" repeatCount="indefinite"/>
  </rect>
  <rect width="{w}" height="{h}" rx="16" fill="none" stroke="{BORDER}" stroke-width="1"/>
  <text x="48" y="42" fill="{BLUE}" font-family="Space Mono, ui-monospace, monospace" font-size="11" font-weight="400" letter-spacing="0.88">PROFILE</text>
  <text x="806" y="42" text-anchor="end" fill="{TEXT_SECONDARY}" font-family="Space Mono, ui-monospace, monospace" font-size="11" font-weight="400" letter-spacing="0.88">REDMOND, WA</text>
  <text x="48" y="118" fill="{TEXT_DISPLAY}" font-family="Doto, Space Mono, monospace" font-size="40" font-weight="700" letter-spacing="-0.8">Maximilian (Manaiakalani) Stein</text>
  <text x="48" y="158" fill="{TEXT_SECONDARY}" font-family="Space Mono, ui-monospace, monospace" font-size="12" font-weight="400" letter-spacing="0.96">PRODUCT MANAGER  /  MICROSOFT</text>
</svg>
'''


def footer_svg() -> str:
    w, h = 854, 140
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="Mahalo — made with aloha in the PNW">
  <defs>
{paint_gradient("fbg", "fglow", reverse=True)}
  </defs>
  <style>
{BANNER_CSS}
  </style>
  <rect width="{w}" height="{h}" rx="16" fill="url(#fbg)"/>
  <rect width="{w}" height="{h}" rx="16" fill="url(#fglow)">
    <animate attributeName="opacity" values="0.85;1;0.85" dur="6s" repeatCount="indefinite"/>
  </rect>
  <rect width="{w}" height="{h}" rx="16" fill="none" stroke="{BORDER}" stroke-width="1"/>
  <text x="48" y="80" fill="{TEXT_DISPLAY}" font-family="Space Grotesk, DM Sans, sans-serif" font-size="24" font-weight="400">Mahalo for stopping by</text>
  <text x="48" y="110" fill="{TEXT_SECONDARY}" font-family="Space Mono, ui-monospace, monospace" font-size="11" font-weight="400" letter-spacing="0.88">BUILT WITH ALOHA  /  REDMOND, WA</text>
</svg>
'''


def wave_svg() -> str:
    w, h = 854, 24
    n = 40
    gap = 2
    x0 = 40
    usable = w - 80
    seg = (usable - gap * (n - 1)) / n
    mid = n // 2
    palette = (BLUE_DEEP, BLUE, PURPLE, GREEN, BLUE)
    rects = []
    x = x0
    for i in range(n):
        dist = abs(i - mid) / mid
        opacity = max(0.15, 1 - dist)
        fill = palette[i % len(palette)] if i == mid else BLUE
        rects.append(
            f'  <rect x="{x:.2f}" y="10" width="{seg:.2f}" height="4" fill="{fill}" opacity="{opacity:.2f}"/>'
        )
        x += seg + gap
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="divider">
{chr(10).join(rects)}
</svg>
'''


def main() -> None:
    (ASSETS / "header.svg").write_text(header_svg(), encoding="utf-8")
    (ASSETS / "footer.svg").write_text(footer_svg(), encoding="utf-8")
    (ASSETS / "wave.svg").write_text(wave_svg(), encoding="utf-8")
    print("wrote assets/header.svg, assets/footer.svg, assets/wave.svg")


if __name__ == "__main__":
    main()
