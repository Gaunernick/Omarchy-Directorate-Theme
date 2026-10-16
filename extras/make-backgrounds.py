#!/usr/bin/env python3
"""DIRECTORATE wallpaper generator.

Writes SVGs designed on a 1920x1080 artboard and renders them at 2x with
rsvg-convert into ../backgrounds/. Re-run after editing:

    python3 make-backgrounds.py

The 24px perimeter band carries measuring ticks so the gap Hyprland leaves
around tiled windows reads as a ruled frame.
"""

import random
import subprocess
from pathlib import Path

W, H = 1920, 1080
BAR = 26       # status bar height
EDGE = 24      # Hyprland gaps_out
FONT = "BlexMono Nerd Font"

VOID = "#111110"
VOID_DEEP = "#0b0b0a"
CONCRETE = "#1d2123"
SLATE = "#2a2e30"
STEEL = "#3a4044"
DIM = "#5c6360"
TEXT = "#b0cbd0"
BRIGHT = "#e7ecec"
CYAN = "#37a8c2"
RED = "#d24646"
AMBER = "#c2a35a"
GREEN = "#4fc98a"
BLUE = "#0e62fe"

HERE = Path(__file__).resolve().parent
OUT = HERE.parent / "backgrounds"
BUILD = HERE / "build"


def text(x, y, s, size=11, fill=DIM, anchor="start", weight="normal", spacing=1.5, opacity=1.0, extra=""):
    return (
        f'<text x="{x}" y="{y}" font-family="{FONT}" font-size="{size}" fill="{fill}" '
        f'text-anchor="{anchor}" font-weight="{weight}" letter-spacing="{spacing}" '
        f'opacity="{opacity}" {extra}>{s}</text>'
    )


def rect(x, y, w, h, fill="none", stroke=None, sw=1, opacity=1.0, extra=""):
    st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ""
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}"{st} opacity="{opacity}" {extra}/>'


def line(x1, y1, x2, y2, stroke=SLATE, sw=1, opacity=1.0):
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{sw}" opacity="{opacity}"/>'


def seal(cx, cy, size, color=TEXT, pupil=CYAN):
    """The Directorate mark: a square aperture with a horizontal slit and a lit pupil."""
    s = size
    h = s / 2
    return "".join([
        rect(cx - h, cy - h, s, s, stroke=color, sw=max(1, s / 22)),
        rect(cx - h * 0.62, cy - s * 0.09, s * 0.62, s * 0.18, fill=color),
        rect(cx + h * 0.10, cy - s * 0.09, s * 0.18, s * 0.18, fill=pupil),
        rect(cx - h * 0.62, cy + s * 0.22, s * 0.25, s * 0.05, fill=color, opacity=0.5),
    ])


def defs():
    return f"""
<defs>
  <linearGradient id="void" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{VOID}"/>
    <stop offset="1" stop-color="{VOID_DEEP}"/>
  </linearGradient>
  <linearGradient id="fog" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0" stop-color="{VOID}" stop-opacity="0"/>
    <stop offset="0.55" stop-color="{VOID}" stop-opacity="0.85"/>
    <stop offset="1" stop-color="{VOID_DEEP}" stop-opacity="1"/>
  </linearGradient>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
    <rect x="11.5" y="11.5" width="1" height="1" fill="{CONCRETE}"/>
  </pattern>
  <pattern id="scan" width="4" height="3" patternUnits="userSpaceOnUse">
    <rect width="4" height="1" fill="#000" opacity="0.18"/>
  </pattern>
  <filter id="glow" x="-20%" y="-20%" width="140%" height="140%">
    <feGaussianBlur stdDeviation="3" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  <filter id="softglow" x="-50%" y="-50%" width="200%" height="200%">
    <feGaussianBlur stdDeviation="8"/>
  </filter>
</defs>"""


def frame(code, title):
    """Ruled perimeter in the band Hyprland leaves free, plus registration marks."""
    out = []
    top = BAR
    # Tick rulers: left/right run down the side bands, bottom runs along the floor.
    for y in range(top, H, 8):
        major = (y - top) % 64 == 0
        ln = 9 if major else 4
        c = STEEL if major else SLATE
        out.append(line(0, y, ln, y, c))
        out.append(line(W - ln, y, W, y, c))
    for x in range(0, W, 8):
        major = x % 64 == 0
        ln = 9 if major else 4
        c = STEEL if major else SLATE
        out.append(line(x, H - ln, x, H, c))
        out.append(line(x, top, x, top + ln, c))
        if x % 256 == 0 and 0 < x < W - 60:
            out.append(text(x + 3, H - 12, f"{x:04d}", size=7, fill=DIM, spacing=0.5))
    # Registration crosshairs at the corners of the work area.
    for (x, y) in [(EDGE, top + EDGE), (W - EDGE, top + EDGE), (EDGE, H - EDGE), (W - EDGE, H - EDGE)]:
        out.append(line(x - 10, y, x + 10, y, STEEL))
        out.append(line(x, y - 10, x, y + 10, STEEL))
    # Sheet identification along the right band, rotated.
    out.append(text(W - 9, H - 120, f"DIRECTORATE // SHEET {code} // {title}", size=8, fill=DIM,
                    spacing=2.5, extra=f'transform="rotate(-90 {W - 9} {H - 120})"'))
    out.append(text(9 + 7, H - 120, "PROPERTY OF THE DIRECTORATE · DO NOT REMOVE", size=8, fill=SLATE,
                    spacing=2.5, extra=f'transform="rotate(-90 16 {H - 120})"'))
    return "".join(out)


def base(body, code, title, scan=True):
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        defs(),
        rect(0, 0, W, H, fill="url(#void)"),
        rect(0, 0, W, H, fill="url(#dots)"),
        body,
        frame(code, title),
    ]
    if scan:
        parts.append(rect(0, 0, W, H, fill="url(#scan)"))
    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------- 1 monolith
def monolith():
    rng = random.Random(7)
    out = []
    cx = W / 2
    ground = 905
    # Inverted ziggurat: every tier is wider than the one beneath it.
    tiers = [  # (top, bottom, width)
        (632, 790, 520),
        (452, 632, 680),
        (222, 452, 860),
    ]
    # Distant blocks on the horizon, same language, smaller.
    for bx, bw, bh in [(220, 180, 260), (420, 120, 190), (1500, 220, 300), (1360, 110, 170), (1730, 140, 220)]:
        out.append(rect(bx, ground - bh, bw, bh, fill="#161819"))
        for wy in range(int(ground - bh + 10), ground - 10, 12):
            for wx in range(bx + 8, bx + bw - 8, 10):
                if rng.random() < 0.05:
                    out.append(rect(wx, wy, 4, 3, fill=CYAN, opacity=0.35))
    # Pilotis.
    for i in range(7):
        x = cx - 230 + i * 76
        out.append(rect(x - 9, 790, 18, ground - 790, fill="#17191a"))
        out.append(rect(x - 9, 790, 2, ground - 790, fill=SLATE))
    # Shadow under the mass.
    out.append(rect(cx - 260, 790, 520, 14, fill="#000", opacity=0.5))

    lit = 0
    red_placed = False
    for ti, (top, bot, w) in enumerate(tiers):
        x0 = cx - w / 2
        out.append(rect(x0, top, w, bot - top, fill="#1a1d1e"))
        out.append(rect(x0, top, w, 2, fill=STEEL))                  # lit slab edge
        out.append(rect(x0, bot - 8, w, 8, fill="#141617"))          # floor slab
        # Window grid: identical cells, endless.
        cw, ch, gx, gy = 12, 8, 6, 7
        cols = int((w - 24) // (cw + gx))
        rows = int((bot - top - 24) // (ch + gy))
        ox = x0 + (w - (cols * (cw + gx) - gx)) / 2
        oy = top + 12
        for r in range(rows):
            for c in range(cols):
                x = ox + c * (cw + gx)
                y = oy + r * (ch + gy)
                roll = rng.random()
                if not red_placed and ti == 2 and r == 3 and c == cols - 9:
                    out.append(rect(x - 3, y - 3, cw + 6, ch + 6, fill=RED, opacity=0.35, extra='filter="url(#softglow)"'))
                    out.append(rect(x, y, cw, ch, fill=RED))
                    red_placed = True
                elif roll < 0.055:
                    out.append(rect(x, y, cw, ch, fill=CYAN, opacity=round(0.45 + rng.random() * 0.45, 2)))
                    lit += 1
                elif roll < 0.062:
                    out.append(rect(x, y, cw, ch, fill=AMBER, opacity=0.55))
                else:
                    out.append(rect(x, y, cw, ch, fill="#0d0e0e"))
        # Vertical fins every few columns.
        for c in range(0, cols + 1, 6):
            fx = ox + c * (cw + gx) - gx / 2 - 1
            out.append(rect(fx, top + 4, 2, bot - top - 12, fill="#232729"))
    # Crown: mast and a signal light.
    out.append(rect(cx - 2, 150, 4, 72, fill=SLATE))
    out.append(rect(cx - 30, 196, 60, 26, fill="#17191a"))
    out.append(rect(cx - 3, 144, 6, 6, fill=RED, extra='filter="url(#glow)"'))
    # Ground plane and fog.
    out.append(rect(0, ground, W, H - ground, fill=VOID_DEEP))
    out.append(line(0, ground, W, ground, STEEL, opacity=0.7))
    out.append(rect(0, 760, W, H - 760, fill="url(#fog)"))
    # Tiny figures crossing the plaza.
    for fx in [880, 905, 1180]:
        out.append(rect(fx, ground - 14, 3, 14, fill="#050505"))
    # Captions.
    out.append(seal(EDGE + 64, BAR + EDGE + 64, 44))
    out.append(text(EDGE + 100, BAR + EDGE + 58, "DIRECTORATE", size=20, fill=BRIGHT, weight="bold", spacing=8))
    out.append(text(EDGE + 100, BAR + EDGE + 78, "CENTRAL ADMINISTRATION · BLOCK 07", size=10, fill=DIM, spacing=3))
    out.append(text(EDGE + 48, H - EDGE - 54, f"OCCUPANCY  4096 / 4096", size=11, fill=TEXT, spacing=2))
    out.append(text(EDGE + 48, H - EDGE - 38, f"STATIONS LIT  {lit:04d}", size=11, fill=CYAN, spacing=2))
    out.append(text(EDGE + 48, H - EDGE - 22, "ALL ACTIVITY IS RECORDED FOR QUALITY ASSURANCE", size=9, fill=DIM, spacing=2))
    out.append(text(W - EDGE - 48, H - EDGE - 22, "PRODUCTIVITY IS PEACE", size=9, fill=DIM, anchor="end", spacing=4))
    return base("".join(out), "01", "MONOLITH")


# ---------------------------------------------------------------- 2 floor plan
def floorplan():
    rng = random.Random(117)
    out = []
    # Isometric floor plane is an affine map, so it renders crisply in SVG.
    ox, oy = 960, 150
    m = "matrix(0.866,0.5,-0.866,0.5,0,0)"
    g = [f'<g transform="translate({ox},{oy}) {m}">']
    cols, rows = 26, 26
    pitch = 44
    station = (13, 8)
    for r in range(rows):
        for c in range(cols):
            x, y = c * pitch, r * pitch
            if c % 6 == 5 or r % 5 == 4:   # aisles
                continue
            you = (c, r) == station
            if you:
                g.append(rect(x - 6, y - 6, pitch + 12, pitch + 12, fill=CYAN, opacity=0.45, extra='filter="url(#softglow)"'))
            g.append(rect(x + 3, y + 3, pitch - 6, pitch - 6, stroke=CYAN if you else SLATE, sw=2 if you else 1,
                          fill="#0f2a31" if you else "#141617"))
            g.append(rect(x + 8, y + 8, 14, 5, fill=CYAN if you else (CYAN if rng.random() < 0.08 else "#24292b"),
                          opacity=1 if you else 0.8))
            g.append(rect(x + 26, y + 18, 8, 8, fill="#0b0b0a"))
    g.append(rect(-20, -20, cols * pitch + 40, rows * pitch + 40, stroke=STEEL, sw=2))
    g.append("</g>")
    out.append("".join(g))
    # Locate the station on screen (apply the same affine map to its centre).
    sx = station[0] * pitch + pitch / 2
    sy = station[1] * pitch + pitch / 2
    px = ox + 0.866 * sx - 0.866 * sy
    py = oy + 0.5 * sx + 0.5 * sy
    # Survey beam up from the station.
    out.append(line(px, py, px, 170, CYAN, 1, 0.8))
    out.append(rect(px - 4, py - 4, 8, 8, fill=CYAN, extra='filter="url(#glow)"'))
    out.append(line(px, 170, px + 40, 170, CYAN, 1, 0.8))
    out.append(text(px + 48, 166, "STATION 0117", size=14, fill=BRIGHT, weight="bold", spacing=3))
    out.append(text(px + 48, 184, "ASSIGNED · OCCUPIED · OBSERVED", size=9, fill=CYAN, spacing=2.5))
    # Fade the far floor into the void.
    out.append(rect(0, 820, W, 260, fill="url(#fog)"))
    out.append(text(EDGE + 48, H - EDGE - 38, "FLOOR 41 · OPEN-PLAN ADMINISTRATION", size=11, fill=TEXT, spacing=2))
    out.append(text(EDGE + 48, H - EDGE - 22, "PERSONNEL SHALL REMAIN AT ASSIGNED STATIONS DURING WORKING HOURS", size=9,
                    fill=DIM, spacing=2))
    out.append(seal(W - EDGE - 64, BAR + EDGE + 64, 44))
    return base("".join(out), "02", "FLOOR PLAN")


# ---------------------------------------------------------------- 3 telemetry
def telemetry():
    import math
    rng = random.Random(3)
    out = []
    # Data wall: columns of figures, fading towards the centre.
    for col in range(0, W, 96):
        for row in range(BAR + 40, H - 40, 16):
            d = abs(col + 48 - W / 2) / (W / 2)
            if rng.random() < 0.55:
                v = f"{rng.randrange(0, 0xFFFFFF):06X}"
                out.append(text(col + 30, row, v, size=10, fill="#1f4d58", spacing=1, opacity=round(0.15 + 0.5 * d, 2)))
    # Oscilloscope.
    gx, gy, gw, gh = 560, 290, 800, 440
    out.append(rect(gx - 12, gy - 12, gw + 24, gh + 24, fill="#0a0c0b", stroke=STEEL))
    for i in range(11):
        out.append(line(gx + i * gw / 10, gy, gx + i * gw / 10, gy + gh, "#1a2b22", 1))
    for j in range(9):
        out.append(line(gx, gy + j * gh / 8, gx + gw, gy + j * gh / 8, "#1a2b22", 1))
    out.append(line(gx + gw / 2, gy, gx + gw / 2, gy + gh, "#24402f", 1))
    out.append(line(gx, gy + gh / 2, gx + gw, gy + gh / 2, "#24402f", 1))

    def trace(fn, color, width, op):
        pts = []
        for i in range(0, 801, 2):
            pts.append(f"{gx + i:.1f},{gy + gh / 2 - fn(i / 800):.1f}")
        p = " ".join(pts)
        return (f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{width * 4}" opacity="{op * 0.25}" filter="url(#softglow)"/>'
                f'<polyline points="{p}" fill="none" stroke="{color}" stroke-width="{width}" opacity="{op}"/>')

    out.append(trace(lambda t: 120 * math.sin(t * 2 * math.pi * 3) * math.exp(-1.2 * t)
                     + 18 * math.sin(t * 2 * math.pi * 41), GREEN, 1.6, 1.0))
    out.append(trace(lambda t: 60 * math.sin(t * 2 * math.pi * 7 + 1.2) - 110, CYAN, 1, 0.7))
    # Alarm spike.
    out.append(trace(lambda t: (150 * math.exp(-((t - 0.73) ** 2) / 0.00008)) + 150 - 300, RED, 1.2, 0.9))
    out.append(text(gx, gy - 24, "CH1  WORKFORCE OUTPUT", size=10, fill=GREEN, spacing=2))
    out.append(text(gx + 260, gy - 24, "CH2  COMPLIANCE", size=10, fill=CYAN, spacing=2))
    out.append(text(gx + gw, gy - 24, "CH3  DEVIATION", size=10, fill=RED, anchor="end", spacing=2))
    # Segmented meters.
    for k, (label, val, color) in enumerate([("MORALE", 0.34, AMBER), ("OUTPUT", 0.92, GREEN),
                                              ("OVERSIGHT", 1.0, CYAN), ("DISSENT", 0.04, RED)]):
        y = gy + gh + 60 + k * 28
        out.append(text(gx, y + 9, label, size=10, fill=DIM, spacing=2))
        segs = 40
        for s in range(segs):
            on = s < round(val * segs)
            out.append(rect(gx + 120 + s * 17, y, 13, 10, fill=color if on else "#1a1d1e", opacity=0.9 if on else 1))
        out.append(text(gx + 120 + segs * 17 + 8, y + 9, f"{int(val * 100):3d}%", size=10, fill=TEXT, spacing=1))
    # Headline.
    out.append(text(gx, gy - 64, "STATUS: NOMINAL", size=34, fill=BRIGHT, weight="bold", spacing=10))
    out.append(text(gx + gw, gy - 64, "DEVIATION 0.003%", size=12, fill=RED, anchor="end", spacing=3))
    return base("".join(out), "03", "TELEMETRY")


# ---------------------------------------------------------------- 4 void
def void():
    out = []
    cx, cy = W / 2, H / 2 + BAR / 2
    out.append(seal(cx, cy - 46, 72))
    out.append(text(cx, cy + 34, "DIRECTORATE", size=26, fill=BRIGHT, anchor="middle", weight="bold", spacing=16))
    out.append(text(cx, cy + 60, "PRODUCTIVITY IS PEACE", size=10, fill=DIM, anchor="middle", spacing=6))
    out.append(line(cx - 160, cy + 80, cx + 160, cy + 80, SLATE))
    return base("".join(out), "04", "VOID", scan=False)


# ---------------------------------------------------------------- 5 institution
def institution():
    """The one sanctioned use of institutional blue: a full-bleed notice."""
    out = [rect(0, 0, W, H, fill=BLUE)]
    # Striped wordmark built from horizontal bars (stencil of the seal).
    for i in range(14):
        y = 300 + i * 34
        out.append(rect(0, y, W, 20, fill="#0a52d8", opacity=0.55))
    out.append(seal(W / 2, H / 2 - 40, 140, color="#e7ecec", pupil="#111110"))
    out.append(text(W / 2, H / 2 + 90, "THE DIRECTORATE THANKS YOU FOR YOUR CONTINUED COMPLIANCE", size=14,
                    fill="#e7ecec", anchor="middle", spacing=5))
    body = "".join(out)
    svg = base(body, "05", "NOTICE", scan=True)
    return svg


SHEETS = {
    "1-monolith": monolith,
    "2-floorplan": floorplan,
    "3-telemetry": telemetry,
    "4-void": void,
    "5-notice": institution,
}


def main():
    BUILD.mkdir(exist_ok=True)
    OUT.mkdir(exist_ok=True)
    for name, fn in SHEETS.items():
        svg = BUILD / f"{name}.svg"
        svg.write_text(fn())
        png = OUT / f"{name}.png"
        subprocess.run(["rsvg-convert", "-w", str(W * 2), "-h", str(H * 2), "-o", str(png), str(svg)], check=True)
        print(png)


if __name__ == "__main__":
    main()
