#!/usr/bin/env python3
"""Sheet 06 · SUPERVISION.

An open-plan floor inside a brutalist footprint, wired like a motherboard.
The desks are three-armed islands on a honeycomb lattice (see
honeycomb_desks.py), joined into rings of five around a chair circle. Every
ring's open side faces the supervision core. Where the building edge, a bus
or an administrator cuts a ring, it survives as a chevron or a fragment.
Each ring is wired from its circle through its opening to a bus in the aisle,
buses feed an administrator's trunk, administrators feed the core. Traces thin
out with every step away from power. One chair is yours, STN-0117: its desk
sector is tinted institutional blue and the route from the core to it is the
only path drawn in signal colour. The chair itself is drawn unlit; the
directorate.beacon shell plugin blinks it (blue at the desk, red on the
screensaver and lock screen) and pulses the route, reading both from
build/6-supervision.seat.json. The sheet has no ruled edge frame.
"""

import json
import math
import random
import sys

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent))
import honeycomb_desks as hd  # noqa: E402

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location("mb", Path(__file__).with_name("make-backgrounds.py"))
_mb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mb)
BAR, BLUE, BRIGHT, CONCRETE, CYAN, DIM, EDGE, H, RED, SLATE, STEEL, TEXT, VOID_DEEP, W = (
    _mb.BAR, _mb.BLUE, _mb.BRIGHT, _mb.CONCRETE, _mb.CYAN, _mb.DIM, _mb.EDGE, _mb.H, _mb.RED, _mb.SLATE,
    _mb.STEEL, _mb.TEXT, _mb.VOID_DEEP, _mb.W)
base, line, rect, seal, text = _mb.base, _mb.line, _mb.rect, _mb.seal, _mb.text

CX, CY = 960, 562

# Building footprint: hard chamfers, a stepped notch top-right, a bitten-off
# corner bottom-left, a recessed loading bay on the bottom edge.
FOOTPRINT = [
    (170, 120), (1210, 120), (1210, 160), (1360, 160), (1360, 120), (1660, 120),
    (1760, 220), (1760, 640), (1800, 640), (1800, 880), (1700, 980),
    (1120, 980), (1120, 940), (800, 940), (800, 980),
    (330, 980), (130, 780), (130, 400), (170, 400),
]

NODES = {  # administrator nodes: centre, label
    "ADM-1": (560, 340),
    "ADM-2": (1360, 340),
    "ADM-3": (560, 790),
    "ADM-4": (1360, 790),
}

A = 44            # lattice spacing (chair circle to chair circle)
ROWS = [-10, -7, -3, 0, 3, 7, 10]   # cup rows (lattice row of their chair circles)
COL_PITCH = 7     # cells from one block column to the next
COL_CELLS = 5     # chair circles per row in a block

DESK_FILL = "#131617"
DESK_FILL_FAR = "#101212"


def inside(px, py, poly=FOOTPRINT):
    hit = False
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % len(poly)]
        if (y1 > py) != (y2 > py) and px < (x2 - x1) * (py - y1) / (y2 - y1) + x1:
            hit = not hit
    return hit


def _seg_dist(px, py, a, b):
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    t = max(0, min(1, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy or 1)))
    return math.hypot(px - (x1 + t * dx), py - (y1 + t * dy))


def primary_routes():
    for nx, ny in NODES.values():
        sx = 1 if nx > CX else -1
        sy = 1 if ny > CY else -1
        yield chamfer((CX + sx * 120, CY + sy * 120), (nx - sx * 60, ny))


def clear(px, py, m=34):
    """Pod fits inside the footprint with a margin, off the core plaza and node pads."""
    for dx, dy in [(-m, -m), (m, -m), (-m, m), (m, m), (0, 0)]:
        if not inside(px + dx, py + dy):
            return False
    if math.hypot(px - CX, py - CY) < 200:
        return False
    if abs(px - CX) < 50 or abs(py - CY) < 40:  # cross aisles
        return False
    for r in primary_routes():
        if any(_seg_dist(px, py, r[i], r[i + 1]) < 40 for i in range(len(r) - 1)):
            return False
    for nx, ny in NODES.values():
        if abs(px - nx) < 84 and abs(py - ny) < 56:
            return False
    return True


def path(points, stroke, sw, opacity=1.0, dash=None):
    d = "M" + " L".join(f"{x:.1f},{y:.1f}" for x, y in points)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<path d="{d}" fill="none" stroke="{stroke}" stroke-width="{sw}" stroke-linejoin="miter" '
            f'opacity="{opacity}"{da}/>')


def via(x, y, r=2.6, color=STEEL, opacity=1.0):
    return f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{VOID_DEEP}" stroke="{color}" stroke-width="1" opacity="{opacity}"/>'


def chamfer(a, b):
    """Route a->b as PCB copper: diagonal first, then straight, 45-degree bends only."""
    (x1, y1), (x2, y2) = a, b
    dx, dy = x2 - x1, y2 - y1
    k = min(abs(dx), abs(dy))
    mid = (x1 + math.copysign(k, dx), y1 + math.copysign(k, dy))
    return [a, mid, b]


def chip(x, y, w, h, label, pins_x, pins_y, color=STEEL, pin=BLUE):
    out = [rect(x - w / 2, y - h / 2, w, h, fill="#141617", stroke=color, sw=1.5)]
    for i in range(pins_x):
        px = x - w / 2 + (i + 0.5) * w / pins_x - 2
        out.append(rect(px, y - h / 2 - 6, 4, 6, fill=pin, opacity=0.8))
        out.append(rect(px, y + h / 2, 4, 6, fill=pin, opacity=0.8))
    for i in range(pins_y):
        py = y - h / 2 + (i + 0.5) * h / pins_y - 2
        out.append(rect(x - w / 2 - 6, py, 6, 4, fill=pin, opacity=0.8))
        out.append(rect(x + w / 2, py, 6, 4, fill=pin, opacity=0.8))
    out.append(rect(x - w / 2 + 5, y - h / 2 + 5, 5, 5, fill=color))  # pin-1 mark
    out.append(text(x, y + 4, label, size=10, fill=TEXT, anchor="middle", spacing=2, weight="bold"))
    return "".join(out)


def lat_y(j):
    return CY + j * A * hd.S3 / 2


def build_floor(lat):
    """Every desk on the floor, keyed to the role it plays: 'core' (supervisors) or 'floor'."""
    core_zone = lambda x, y: abs(x - CX) < A * 4.6 and abs(y - CY) < A * 3.4
    floor, cups = set(), []   # cups: (i, j, opens_up)
    for j in ROWS:
        for k in range(-4, 5):
            i0 = round(k * COL_PITCH - j / 2) - COL_CELLS // 2
            first_up = (k + j) % 2 == 0
            for n in hd.cup_row(lat, i0, j, COL_CELLS, first_up=first_up):
                hx, hy = lat.hub(n)
                if core_zone(hx, hy) and j == 0:
                    continue
                floor.add(n)
            for c in range(COL_CELLS):
                cups.append((i0 + c, j, (c % 2 == 0) == first_up))
    # The supervision group: a C either side of the mainframe, a pendant from each axis row pointing in.
    core = set(hd.half_ring(lat, -2, 0, 1)) | set(hd.half_ring(lat, 2, 0, -1))
    for j, down in ((-3, True), (3, False)):
        target = (CX, lat_y(j + (1 if down else -1)))
        cands = [n for n in floor if n[0] == ("d" if down else "u") and abs(lat.hub(n)[1] - target[1]) < A
                 and abs(lat.hub(n)[0] - CX) < A]
        if cands:
            anchor = min(cands, key=lambda n: (abs(lat.hub(n)[0] - CX), lat.hub(n)))
            core |= set(hd.pendant(lat, anchor, down=down))
    floor -= core
    # The building cuts the pattern.
    keep = lambda n: all(inside(lat.hub(n)[0] + dx, lat.hub(n)[1] + dy)
                         for dx, dy in [(-A * .5, -A * .5), (A * .5, -A * .5), (-A * .5, A * .5), (A * .5, A * .5)])
    floor = {n for n in floor if keep(n)}
    cups = [(i, j, up) for i, j, up in cups if inside(*lat.cell(i, j)) and not core_zone(*lat.cell(i, j))]
    return floor, core, cups


def supervision():
    lat = hd.Lattice(A, ox=CX, oy=CY)
    floor_layer, traces, lit_traces, desks, labels, callout = [], [], [], [], [], []

    pts = " ".join(f"{x},{y}" for x, y in FOOTPRINT)
    floor_layer.append(f'<polygon points="{pts}" fill="#0e1010" stroke="{STEEL}" stroke-width="7" stroke-linejoin="miter"/>')
    floor_layer.append(f'<polygon points="{pts}" fill="none" stroke="{VOID_DEEP}" stroke-width="2" stroke-linejoin="miter"/>')

    floor, core, cups = build_floor(lat)
    everything = floor | core

    # ---- wiring: trunks in the column gaps, buses in the wide aisles, a lead out of every cup.
    gaps_x = [CX + (k + 0.5) * COL_PITCH * A for k in range(-4, 4)]
    aisles_y = [lat_y(-5), lat_y(5)]
    top, bot = 140, 970
    for gx in gaps_x:
        d = abs(gx - CX) / (COL_PITCH * A)
        traces.append(path([(gx, top), (gx, bot)], STEEL if d < 1 else SLATE, max(0.8, 2.6 - d * 0.6),
                           max(0.35, 1 - d * 0.18)))
    for ay in aisles_y:
        traces.append(path([(gaps_x[0], ay), (gaps_x[-1], ay)], STEEL, 2.2))
        for gx in gaps_x:
            traces.append(via(gx, ay, 2.8, STEEL))
    # Mainframe -> the two inner trunks, twin conductors.
    for sx in (-1, 1):
        gx = CX + sx * 0.5 * COL_PITCH * A
        for off in (-5, 5):
            traces.append(path([(CX + sx * 40, CY + off), (gx - sx * 30, CY + off), (gx, CY + off - 30 * (1 if off < 0 else -1))],
                               STEEL, 2.6))
    for i, j, up in cups:
        cx, cy = lat.cell(i, j)
        ly = lat_y(j + (-1.5 if up else 1.5))
        d = math.hypot(cx - CX, cy - CY) / 900
        traces.append(path([(cx, cy), (cx, ly)], SLATE, 0.9, max(0.3, 0.9 - d)))
        traces.append(via(cx, cy, 2.0, SLATE, max(0.3, 0.9 - d)))
        traces.append(via(cx, ly, 1.4, SLATE, max(0.3, 0.9 - d)))

    # ---- you and the vacancy
    def cup_near(tx, ty, opens_up):
        return min((c for c in cups if c[2] == opens_up),
                   key=lambda c: math.hypot(lat.cell(c[0], c[1])[0] - tx, lat.cell(c[0], c[1])[1] - ty))

    yi, yj, yup = cup_near(1560, 300, False)
    you_node = min((n for n in floor if (yi, yj) in lat.corners(n)), key=lambda n: (-lat.hub(n)[0], lat.hub(n)[1]))  # tie-break: set order is hash-seeded
    you_point, you_deg = lat.seat(you_node, (yi, yj))
    ycx, ycy = lat.cell(yi, yj)
    ly = lat_y(yj + 1.5)
    gx = min((g for g in gaps_x if g > CX), key=lambda g: abs(g - ycx + A))
    inner = CX + 0.5 * COL_PITCH * A
    route = [(CX + 40, CY - 5), (inner - 30, CY - 5), (inner, CY - 35), (inner, aisles_y[0]),
             (gx, aisles_y[0]), (gx, ly), (ycx, ly), (ycx, ycy)]
    # Drawn at rest; the beacon pulses it on top while you are at your seat.
    lit_traces.append(path(route, CYAN, 1.5, 0.5))
    (Path(__file__).resolve().parent / "build" / "6-supervision.seat.json").write_text(json.dumps({
        "artboard": [W, H], "x": round(you_point[0], 1), "y": round(you_point[1], 1),
        "deg": round(you_deg + 90, 1), "size": round(lat.chair_size(), 2),
        "route": [[round(x, 1), round(y, 1)] for x, y in route],
        "active": BLUE, "away": RED, "link": CYAN}) + "\n")

    # ---- desks, quieter with distance from the mainframe
    def ring_of(n):
        hx, hy = lat.hub(n)
        return 0 if math.hypot((hx - CX) / 1.6, hy - CY) < 330 else 1

    for band in (0, 1):
        group = [n for n in floor if ring_of(n) == band]
        desks.append(hd.draw_cluster(
            lat, group,
            desk_fill=DESK_FILL if band == 0 else DESK_FILL_FAR,
            desk_stroke=STEEL if band == 0 else "#30363a",
            open_stroke="#5a6266" if band == 0 else STEEL,
            divider=SLATE if band == 0 else CONCRETE,
            chair_stroke="#4a5256" if band == 0 else SLATE,
            sw=0.9, open_sw=2.2, context=everything))
    # STN-0117: the desk sector is tinted; the chair is left unlit for the beacon to blink.
    desks.append(f'<polygon points="{hd.poly(lat.sector(you_node, (yi, yj)))}" fill="{BLUE}" opacity="0.3"/>')
    desks.append(hd.draw_cluster(lat, core, desk_fill="#0d1526", desk_stroke=BLUE, open_stroke=BLUE,
                                 divider="#1d3a78", chair_stroke=BLUE, sw=1.1, open_sw=2.6, context=everything))

    # ---- mainframe: a diamond die in the middle of its supervisors
    m = A * 0.95
    core_g = [f'<circle cx="{CX}" cy="{CY}" r="{A * 1.4:.1f}" fill="{BLUE}" opacity="0.22" filter="url(#softglow)"/>',
              f'<rect x="{-m / 2:.1f}" y="{-m / 2:.1f}" width="{m:.1f}" height="{m:.1f}" fill="#0b1224" stroke="{BLUE}" '
              f'stroke-width="1.6" transform="translate({CX},{CY}) rotate(45)"/>',
              f'<rect x="{-m * 0.32:.1f}" y="{-m * 0.32:.1f}" width="{m * 0.64:.1f}" height="{m * 0.64:.1f}" fill="none" '
              f'stroke="{BLUE}" stroke-width="0.8" opacity="0.7" transform="translate({CX},{CY}) rotate(45)"/>',
              text(CX, CY + 3, "S-00", size=8, fill=BRIGHT, anchor="middle", spacing=1.5, weight="bold")]
    labels.append(text(CX, 962, "MAINFRAME · SUPERVISION", size=10, fill=BRIGHT, anchor="middle", spacing=3, weight="bold"))
    labels.append(text(CX, 975, "ALL STATIONS REPORT TO CORE", size=7, fill=DIM, anchor="middle", spacing=2.2))

    # Your station callout.
    if True:
        px, py = you_point
        ly = 86
        callout.append(path([(px, py), (px, ly), (px - 24, ly)], CYAN, 1, 0.85))
        callout.append(text(px - 34, ly + 1, "STN-0117", size=14, fill=BRIGHT, anchor="end", spacing=3, weight="bold"))
        callout.append(text(px - 34, ly + 18, "ROUTED · ASSIGNED · REPLACEABLE", size=9, fill=CYAN, anchor="end", spacing=2.5))

    clip = f'<clipPath id="footprint"><polygon points="{pts}"/></clipPath>'
    traces = [clip, '<g clip-path="url(#footprint)">'] + traces + ['</g>']
    body = "".join(floor_layer + traces + lit_traces + desks + core_g + labels + callout)
    body += text(EDGE + 48, H - EDGE - 38, "FLOOR 41 · CENTRALISED SUPERVISION", size=11, fill=TEXT, spacing=2)
    body += text(EDGE + 48, H - EDGE - 22, "SIGNAL FLOWS OUTWARD · ACCOUNTABILITY FLOWS INWARD", size=9, fill=DIM, spacing=2)
    body += seal(W - EDGE - 64, BAR + EDGE + 64, 44)
    return base(body, "06", "SUPERVISION", framed=False)
