#!/usr/bin/env python3
# Generates the Israeli theme wallpapers and lock logo as SVG, rendered with rsvg-convert + ImageMagick.
# Usage: python3 wallpapers.py [startup_nation gal aryeh kachol_lavan silicon_wadi unlock]
import math, random, re, subprocess, sys, pathlib, tempfile

OUT = pathlib.Path(__file__).resolve().parent
TMP = pathlib.Path(tempfile.mkdtemp(prefix="israeli-theme-"))
(OUT / "backgrounds").mkdir(parents=True, exist_ok=True)
W, H = 3840, 2160
TEKHELET, WHITE, NIGHT = "#3d7eff", "#eaf2ff", "#050b26"
STRIPES, BAND = (H * 2 / 11, H * 9 / 11), H * 1.4 / 11  # flag proportions


def star_pts(cx, cy, r, up=True):
    s = -1 if up else 1
    return [(cx, cy + s * r), (cx + r * 0.8660254, cy - s * r / 2), (cx - r * 0.8660254, cy - s * r / 2)]


def poly(pts):
    return " ".join(f"{x:.1f},{y:.1f}" for x, y in pts)


def triangles(cx, cy, r):
    return "".join(f'<polygon points="{poly(star_pts(cx, cy, r, up))}"/>' for up in (True, False))


def tube(shapes, width, color=TEKHELET, core=WHITE):
    """Neon tube: a wide coloured stroke under a thin white core, both glowing."""
    return (f'<g filter="url(#glow)" fill="none" stroke-linejoin="round" stroke-linecap="round">'
            f'<g stroke="{color}" stroke-width="{width * 2.6:.1f}">{shapes}</g><g stroke="{core}" stroke-width="{width:.1f}">{shapes}</g></g>')


def neon_canvas(seed, *defs):
    rng = random.Random(seed)
    d = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}"><defs>',
         f'<filter id="glow" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}">'
         '<feGaussianBlur in="SourceGraphic" stdDeviation="55" result="b2"/><feGaussianBlur in="SourceGraphic" stdDeviation="12" result="b1"/>'
         '<feMerge><feMergeNode in="b2"/><feMergeNode in="b2"/><feMergeNode in="b1"/><feMergeNode in="SourceGraphic"/></feMerge></filter>',
         f'<filter id="soft" filterUnits="userSpaceOnUse" x="0" y="0" width="{W}" height="{H}"><feGaussianBlur stdDeviation="150"/></filter>',
         '<radialGradient id="bg" cx="0.5" cy="0.5" r="0.75"><stop offset="0" stop-color="#0d1c55"/><stop offset="0.55" stop-color="#050b26"/><stop offset="1" stop-color="#01020a"/></radialGradient>',
         '<pattern id="dots" width="64" height="64" patternUnits="userSpaceOnUse"><circle cx="32" cy="32" r="2.2" fill="#3d7eff" opacity="0.22"/></pattern>',
         *defs, "</defs>",
         f'<rect width="{W}" height="{H}" fill="url(#bg)"/><rect width="{W}" height="{H}" fill="url(#dots)"/>']
    for _ in range(160):
        x, y = rng.uniform(0, W), rng.uniform(0, H)
        r = rng.choice([1.2, 1.6, 2.2, 2.2, 3, 4.5])
        d.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="#fff" opacity="{rng.uniform(0.25, 1.0) * (1 - y / H * 0.7):.2f}"/>')
    return d, rng


def lasers(d, curve=None):
    """The flag's two stripes as light beams; curve(y) returns a path along y (straight by default)."""
    curve = curve or (lambda y: f"M-200,{y:.0f} H{W + 200}")
    for yc in STRIPES:
        d.append(f'<path d="{curve(yc)}" stroke="{TEKHELET}" stroke-width="{BAND:.0f}" fill="none" opacity="0.28" filter="url(#soft)"/>')
        d.append(f'<g filter="url(#glow)" fill="none"><path d="{curve(yc - BAND / 2 + 5)}" stroke="{TEKHELET}" stroke-width="10"/>'
                 f'<path d="{curve(yc + BAND / 2 - 5)}" stroke="{TEKHELET}" stroke-width="10"/>'
                 f'<path d="{curve(yc)}" stroke="{WHITE}" stroke-width="6" opacity="0.8"/></g>')


def halo(d, cx, cy, r):
    d.append(f'<circle cx="{cx:.0f}" cy="{cy:.0f}" r="{r}" fill="{TEKHELET}" opacity="0.35" filter="url(#soft)"/>')


def finish(d, name, caption):
    d.append(f'<text x="{W / 2}" y="{H - 90}" text-anchor="middle" font-family="JetBrainsMono Nerd Font, monospace" font-size="38" letter-spacing="18" fill="{WHITE}" opacity="0.45">{caption}</text></svg>')
    return render(name, "".join(d))


def render(name, svg, jpg=True):
    src = TMP / f"{name}.svg"
    src.write_text(svg)
    png = TMP / f"{name}.png"
    subprocess.run(["rsvg-convert", str(src), "-o", str(png)], check=True)
    if jpg:
        subprocess.run(["magick", str(png), "-quality", "92", str(OUT / "backgrounds" / f"{name}.jpg")], check=True)
    return png


# ---------------------------------------------------------------- 1. the flag, lit
def startup_nation():
    d, _ = neon_canvas(5708)
    lasers(d)
    halo(d, W / 2, H / 2, 620)
    d.append(tube(triangles(W / 2, H / 2, 480), 22))
    return finish(d, "1-startup-nation", "STARTUP · NATION")


# ---------------------------------------------------------------- 2. the flag, waving
def gal():
    d, _ = neon_canvas(1897)
    lam, phi = 2900, 1.2
    dy = lambda x, lag=0.0: (50 + 150 * x / W) * math.sin(2 * math.pi * x / lam - phi - lag)
    xs = range(-40, W + 41, 24)
    for lag, opacity in ((0.7, 0.14), (0.35, 0.3)):  # motion echoes trailing the wave
        path = lambda y, lag=lag: "M" + " L".join(f"{x},{y + dy(x, lag):.1f}" for x in xs)
        d.append(f'<g opacity="{opacity}">')
        lasers(d, path)
        d.append("</g>")
    lasers(d, lambda y: "M" + " L".join(f"{x},{y + dy(x):.1f}" for x in xs))

    def bent(up):  # the star rides the same wave
        pts = star_pts(W / 2, H / 2, 480, up)
        seq = [(a[0] + (b[0] - a[0]) * k / 40, a[1] + (b[1] - a[1]) * k / 40) for a, b in zip(pts, pts[1:] + pts[:1]) for k in range(40)]
        return f'<polygon points="{poly([(x, y + dy(x)) for x, y in seq])}"/>'
    halo(d, W / 2, H / 2 + dy(W / 2), 620)
    d.append(tube(bent(True) + bent(False), 22))
    return finish(d, "2-gal", "I · S · R · A · E · L")


# ---------------------------------------------------------------- 3. the Lion of Judah as a neon sign
def aryeh():
    src = (OUT / "lion.svg").read_text()
    paths = re.findall(r'<path\s+style="fill:(#[0-9a-f]{6})[^"]*"\s+d="([^"]+)"', src)
    body = "".join(f'<path d="{p}"/>' for c, p in paths if c == "#edd400")
    tongue = "".join(f'<path d="{p}"/>' for c, p in paths if c == "#cc0000")
    d, _ = neon_canvas(1950)
    lasers(d)
    ls = 2.35
    lx, ly = W / 2 - 200 * ls, H / 2 - 225 * ls
    halo(d, W / 2, H / 2, 560)
    place = lambda shapes: f'<g transform="translate({lx:.0f},{ly:.0f}) scale({ls})">{shapes}</g>'  # glow outside the scale, or it gets clipped
    d.append(tube(place(body), 2.0) + f'<g filter="url(#glow)" fill="{TEKHELET}">{place(tongue)}</g>')
    return finish(d, "3-aryeh-yehuda", "LION · OF · JUDAH")


# ---------------------------------------------------------------- 4. a wall of neon flags
def kachol_lavan():
    d, rng = neon_canvas(1948)
    cols, rows, tw, gap = 7, 5, 380, 110
    th, u = tw * 160 / 220, tw / 220
    x0 = (W - cols * tw - (cols - 1) * gap) / 2
    y0 = (H - 70 - rows * th - (rows - 1) * gap) / 2
    lit = {1.0: [], 0.55: [], 0.15: []}
    for r in range(rows):
        for c in range(cols):
            x, y = x0 + c * (tw + gap), y0 + r * (th + gap)
            level = rng.choices(list(lit), weights=[7, 2, 1])[0]
            lit[level].append((x, y))
    for level, tiles in lit.items():
        frames = "".join(f'<rect x="{x:.0f}" y="{y:.0f}" width="{tw}" height="{th:.0f}" rx="14"/>' for x, y in tiles)
        stripes = "".join(f'<path d="M{x + 30:.0f},{y + v * u:.0f} H{x + tw - 30:.0f}"/>' for x, y in tiles for v in (27.5, 132.5))
        stars = "".join(triangles(x + tw / 2, y + th / 2, 25 * u) for x, y in tiles)
        d.append(f'<g opacity="{level}"><g filter="url(#glow)" fill="none" stroke="{TEKHELET}" stroke-width="4" opacity="0.6">{frames}</g>'
                 f'{tube(stripes, 8)}{tube(stars, 5)}</g>')
    return finish(d, "4-kachol-lavan", "BLUE · AND · WHITE")


# ---------------------------------------------------------------- 5. the star on a circuit board
def silicon_wadi():
    d, rng = neon_canvas(1993)
    lasers(d)
    cx, cy, r, s = W / 2, H / 2, 360, 40
    bus_top, bus_bottom = STRIPES[0] + BAND / 2, STRIPES[1] - BAND / 2
    traces, pads = [], []

    def trace(*pts):
        traces.append("M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts))
        pads.extend([pts[0], pts[-1]])

    # top and bottom points of the star run straight to the stripes
    for k in (-1, 0, 1):
        trace((cx + k * s, cy - r - abs(k) * 50), (cx + k * s, bus_top))
        trace((cx + k * s, cy + r + abs(k) * 50), (cx + k * s, bus_bottom))
    # side points run out, then bend 45° onto the nearer stripe
    for sx in (-1, 1):
        for sy in (-1, 1):
            vx, vy = cx + sx * r * 0.8660254, cy + sy * r / 2
            bus = bus_top if sy < 0 else bus_bottom
            for k in (-1, 0, 1):
                y = vy + k * s
                start = (vx + sx * (60 + abs(k) * 30), y)
                bend = vx + sx * (520 - sy * k * s * (math.sqrt(2) - 1))
                trace(start, (bend, y), (bend + sx * abs(bus - y), bus))
            # and one long trace out to the edge of the board
            y = vy + sy * 150
            trace((vx + sx * 40, y), (vx + sx * 1100, y), (vx + sx * 1100 + sx * 180, y + sy * 180), (cx + sx * (W / 2 + 40), y + sy * 180))
    # pins off the outside of each stripe
    for bus, direction in ((STRIPES[0] - BAND / 2, -1), (STRIPES[1] + BAND / 2, 1)):
        for x in range(160, W, 150):
            if rng.random() < 0.45:
                trace((x, bus), (x, bus + direction * rng.choice([70, 110, 150])))
    halo(d, cx, cy, 520)
    d.append(f'<g filter="url(#glow)" fill="none" stroke="{TEKHELET}" stroke-width="6" stroke-linejoin="round">{"".join(f"<path d=\"{t}\"/>" for t in traces)}</g>')
    d.append(f'<g fill="{NIGHT}" stroke="{WHITE}" stroke-width="5">{"".join(f"<circle cx=\"{x:.0f}\" cy=\"{y:.0f}\" r=\"11\"/>" for x, y in pads)}</g>')
    d.append(tube(triangles(cx, cy, r), 18))
    return finish(d, "5-silicon-wadi", "SILICON · WADI")


# ---------------------------------------------------------------- lock screen logo
def unlock():
    uw, uh = 1100, 267
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{uw}" height="{uh}" viewBox="0 0 {uw} {uh}">'
           f'<g fill="none" stroke="{TEKHELET}" stroke-width="20" stroke-linejoin="round">{triangles(133, 133, 108)}</g>'
           f'<text x="640" y="200" text-anchor="middle" font-family="Noto Sans Hebrew" font-weight="900" font-size="235" fill="{WHITE}">ישראל</text></svg>')
    png = render("unlock", svg, jpg=False)
    subprocess.run(["magick", str(png), "-trim", "+repage", "-bordercolor", "none", "-border", "8", str(OUT / "unlock.png")], check=True)


for fn in sys.argv[1:] or ["startup_nation", "gal", "aryeh", "kachol_lavan", "silicon_wadi", "unlock"]:
    globals()[fn]()
    print("rendered", fn)
