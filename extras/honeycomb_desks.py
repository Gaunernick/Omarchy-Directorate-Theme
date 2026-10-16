"""Honeycomb desk geometry for the SUPERVISION sheet.

Cell centres sit on a triangular lattice with spacing A. Every triangle of that
lattice is one desk node: a three-armed island whose arms point at the three
neighbouring triangles. Each node is its triangle minus a disc of radius R
around every corner, so the corners become concave chair bays and the middle
of every edge survives as a flat face. Two nodes that share an edge are joined
desks (a seam); a face with no neighbour is open, the red edge in the reference
plans: an aisle to walk in by, or a port for another cluster.
"""

import math

S3 = math.sqrt(3)


class Lattice:
    def __init__(self, a, ox=0.0, oy=0.0, r_ratio=0.38):
        self.a = a
        self.r = a * r_ratio          # chair-bay radius; face width = a - 2r
        self.ox, self.oy = ox, oy

    # cell centre (i, j) on the triangular lattice, rows horizontal
    def cell(self, i, j):
        return (self.ox + self.a * (i + j / 2), self.oy + self.a * j * S3 / 2)

    def cell_at(self, x, y):
        j = round((y - self.oy) / (self.a * S3 / 2))
        i = round((x - self.ox) / self.a - j / 2)
        return i, j

    # node = triangle: ("u", i, j) -> (i,j),(i+1,j),(i,j+1); ("d", i, j) -> (i+1,j),(i,j+1),(i+1,j+1)
    def corners(self, node):
        t, i, j = node
        if t == "u":
            return [(i, j), (i + 1, j), (i, j + 1)]
        return [(i + 1, j), (i, j + 1), (i + 1, j + 1)]

    def hub(self, node):
        pts = [self.cell(*c) for c in self.corners(node)]
        return (sum(p[0] for p in pts) / 3, sum(p[1] for p in pts) / 3)

    def neighbours(self, node):
        t, i, j = node
        if t == "u":
            return [("d", i, j), ("d", i - 1, j), ("d", i, j - 1)]
        return [("u", i, j), ("u", i + 1, j), ("u", i, j + 1)]

    def nodes_around(self, i, j):
        """The six triangles that share cell (i, j), in angular order."""
        return [("u", i, j), ("d", i - 1, j), ("u", i - 1, j), ("d", i - 1, j - 1), ("u", i, j - 1), ("d", i, j - 1)]

    def edges(self, node):
        """Each edge as (cellA, cellB, neighbour sharing it)."""
        c = self.corners(node)
        out = []
        for k in range(3):
            e = {c[k], c[(k + 1) % 3]}
            for n in self.neighbours(node):
                if e <= set(self.corners(n)):
                    out.append((c[k], c[(k + 1) % 3], n))
        return out

    # ---------------------------------------------------------------- geometry
    def outline(self, node, steps=10):
        """Closed polygon: three faces joined by concave arcs around the corners."""
        c = [self.cell(*k) for k in self.corners(node)]
        r = self.r
        pts = []
        for k in range(3):
            p0, p1, p2 = c[k], c[(k + 1) % 3], c[(k + 2) % 3]
            # face along edge p0 -> p1, trimmed by r at both ends
            ux, uy = (p1[0] - p0[0]) / self.a, (p1[1] - p0[1]) / self.a
            pts.append((p0[0] + ux * r, p0[1] + uy * r))
            pts.append((p1[0] - ux * r, p1[1] - uy * r))
            # arc around p1 from edge p1->p0 to edge p1->p2 (60 degrees, inside the triangle)
            a0 = math.atan2(p0[1] - p1[1], p0[0] - p1[0])
            a1 = math.atan2(p2[1] - p1[1], p2[0] - p1[0])
            d = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
            for s in range(1, steps):
                a = a0 + d * s / steps
                pts.append((p1[0] + math.cos(a) * r, p1[1] + math.sin(a) * r))
        return pts

    def face(self, ca, cb):
        p0, p1 = self.cell(*ca), self.cell(*cb)
        ux, uy = (p1[0] - p0[0]) / self.a, (p1[1] - p0[1]) / self.a
        return (p0[0] + ux * self.r, p0[1] + uy * self.r), (p1[0] - ux * self.r, p1[1] - uy * self.r)

    def chair_size(self):
        return self.a * 0.09

    def seat(self, node, corner):
        """Chair position in the bay at `corner`, pulled up to the desk edge, facing the hub."""
        hx, hy = self.hub(node)
        cx, cy = self.cell(*corner)
        ang = math.atan2(hy - cy, hx - cx)
        d = self.r - self.chair_size() * 0.75
        return (cx + math.cos(ang) * d, cy + math.sin(ang) * d), math.degrees(ang)

    def sector(self, node, corner, steps=10):
        """The workstation facing one chair bay: hub, two face midpoints, and the arc between them."""
        cs = self.corners(node)
        k = cs.index(corner)
        prev_c, next_c = cs[(k - 1) % 3], cs[(k + 1) % 3]
        hx, hy = self.hub(node)
        p = self.cell(*corner)
        m0 = [(a + b) / 2 for a, b in zip(self.cell(*prev_c), p)]
        m1 = [(a + b) / 2 for a, b in zip(p, self.cell(*next_c))]
        q0 = self.cell(*prev_c)
        q1 = self.cell(*next_c)
        a0 = math.atan2(q0[1] - p[1], q0[0] - p[0])
        a1 = math.atan2(q1[1] - p[1], q1[0] - p[0])
        d = (a1 - a0 + math.pi) % (2 * math.pi) - math.pi
        arc = [(p[0] + math.cos(a0 + d * s / steps) * self.r, p[1] + math.sin(a0 + d * s / steps) * self.r)
               for s in range(steps + 1)]
        return [(hx, hy), tuple(m0)] + arc + [tuple(m1)]


def poly(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def chair(x, y, deg, s, stroke, fill="none", sw=1):
    """Top-down office chair: seat with a backrest on the side away from the desk."""
    return (f'<g transform="translate({x:.1f},{y:.1f}) rotate({deg + 90:.1f})">'
            f'<rect x="{-s * 0.5:.2f}" y="{-s * 0.42:.2f}" width="{s:.2f}" height="{s * 0.8:.2f}" rx="{s * 0.2:.2f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
            f'<rect x="{-s * 0.55:.2f}" y="{s * 0.42:.2f}" width="{s * 1.1:.2f}" height="{s * 0.28:.2f}" rx="{s * 0.1:.2f}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/></g>')


def draw_cluster(lat, nodes, desk_fill, desk_stroke, open_stroke, divider, chair_stroke,
                 sw=1.0, open_sw=2.2, chair_size=None, lit=None, lit_color=None, glow=True, context=None):
    """Render a set of nodes: islands, seams, open faces, dividers, chairs.

    `context` is every node on the floor, so a seam to a neighbouring cluster is not drawn as open.
    """
    nodes = set(nodes)
    context = set(context) if context else nodes
    cs = chair_size or lat.chair_size()
    out = []
    lit_node, lit_corner = lit if lit else (None, None)
    for n in nodes:
        out.append(f'<polygon points="{poly(lat.outline(n))}" fill="{desk_fill}" stroke="{desk_stroke}" '
                   f'stroke-width="{sw}" stroke-linejoin="miter"/>')
    for n in nodes:
        if n == lit_node:
            out.append(f'<polygon points="{poly(lat.sector(n, lit_corner))}" fill="{lit_color}" opacity="0.35"/>')
        hx, hy = lat.hub(n)
        for ca, cb, nb in lat.edges(n):
            (x0, y0), (x1, y1) = lat.face(ca, cb)
            mx, my = (x0 + x1) / 2, (y0 + y1) / 2
            out.append(f'<line x1="{hx:.1f}" y1="{hy:.1f}" x2="{mx:.1f}" y2="{my:.1f}" stroke="{divider}" '
                       f'stroke-width="{sw * 0.8}"/>')
            if nb not in context:
                out.append(f'<line x1="{x0:.1f}" y1="{y0:.1f}" x2="{x1:.1f}" y2="{y1:.1f}" stroke="{open_stroke}" '
                           f'stroke-width="{open_sw}"/>')
    for n in nodes:
        for c in lat.corners(n):
            (x, y), deg = lat.seat(n, c)
            if n == lit_node and c == lit_corner:
                if glow:
                    out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{cs * 1.8:.1f}" fill="{lit_color}" opacity="0.6" '
                               f'filter="url(#softglow)"/>')
                out.append(chair(x, y, deg, cs, lit_color, fill=lit_color))
            else:
                out.append(chair(x, y, deg, cs, chair_stroke, sw=0.8))
    return "".join(out)


def ring(lat, i, j, gap_dir=None):
    """Five or six nodes around cell (i, j); drop the one pointing along gap_dir (radians)."""
    around = lat.nodes_around(i, j)
    if gap_dir is None:
        return around
    cx, cy = lat.cell(i, j)

    def off(n):
        hx, hy = lat.hub(n)
        a = math.atan2(hy - cy, hx - cx)
        return abs((a - gap_dir + math.pi) % (2 * math.pi) - math.pi)

    gap = min(around, key=off)
    return [n for n in around if n != gap]


# ---------------------------------------------------------------- compositions
def strip(i0, j, n):
    """A zigzag run along one row band: n desks, arms alternating up and down."""
    out = []
    for k in range(n):
        i = i0 + k // 2
        out.append(("u", i, j) if k % 2 == 0 else ("d", i, j))
    return out


def pair(i0, j, n):
    """Two strips one empty band apart: their chair bays face each other across a narrow aisle."""
    return strip(i0, j, n) + strip(i0 - 1, j + 2, n)


def pendant(lat, node, down=True):
    """A chevron hung off one desk: the desk in the next band sharing its face, plus that desk's two flanks."""
    t, i, j = node
    if down:
        if t != "d":
            raise ValueError("a downward pendant hangs off a 'd' desk (its open face points down)")
        head = ("u", i, j + 1)
    else:
        if t != "u":
            raise ValueError("an upward pendant hangs off a 'u' desk (its open face points up)")
        head = ("d", i, j - 1)
    flanks = [n for n in lat.neighbours(head) if n != node]
    return [head] + flanks


def half_ring(lat, i, j, side):
    """Four desks around cell (i, j) forming a C that opens towards `side` (+1 right, -1 left)."""
    cx, _ = lat.cell(i, j)
    around = lat.nodes_around(i, j)
    return [n for n in around if (lat.hub(n)[0] - cx) * side < lat.a * 0.1]


def node_toward(lat, i, j, deg):
    """The desk around cell (i, j) whose hub lies in direction `deg` (screen degrees, 90 = down)."""
    cx, cy = lat.cell(i, j)
    t = math.radians(deg)

    def off(n):
        hx, hy = lat.hub(n)
        a = math.atan2(hy - cy, hx - cx)
        return abs((a - t + math.pi) % (2 * math.pi) - math.pi)

    return min(lat.nodes_around(i, j), key=off)


def cup_row(lat, i0, j, cells, first_up=True):
    """A run of chair circles along cell row j, wrapped in desks, each circle opened as a cup.

    Cups alternate: open upwards, open downwards, ... The result is the ornate double row from the
    reference plans: deep bays on both sides, arms reaching up and down between them.
    """
    nodes = set()
    for k in range(cells):
        nodes.update(lat.nodes_around(i0 + k, j))
    for k in range(cells):
        up = (k % 2 == 0) == first_up
        nodes.discard(node_toward(lat, i0 + k, j, -90 if up else 90))
    return sorted(nodes)
