# Where Maine's wood goes: exports by country (2024) with an inset of net shipments to U.S. states (2022).
# Rebuilt November 11, 2026, so the whole Southern Hemisphere shows and the U.S. inset sits on the same bubble scale.
# Inputs (same folder):
#   2024_maine-wood-exports-by-country_DATA.csv        U.S. Census Bureau, USA Trade Online, HS 44, 47, 48, origin Maine
#   2022_maine-net-shipments-to-states-cfs_DATA.csv    2022 Commodity Flow Survey, SCTG 25 to 28, with coefficients of variation
# Usage: python3 <script> <node_modules dir with world-atlas and us-atlas> <out.png>
import csv, json, sys, math, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, Circle
from matplotlib.path import Path
import matplotlib.patheffects as pe

HERE = os.path.dirname(os.path.abspath(__file__))
ATLAS, OUT = sys.argv[1], sys.argv[2]
plt.rcParams["font.family"] = "Liberation Sans"
GRN, NAV, ORG = "#1F4D36", "#2F6C9E", "#D9692E"
LAND, SEA, INK, GRY = "#E8E6E1", "#FFFFFF", "#2B2B2B", "#6E6E6E"
halo = [pe.withStroke(linewidth=2.6, foreground="white")]


def topo(path, obj):
    t = json.load(open(path))
    sc, tr = t["transform"]["scale"], t["transform"]["translate"]
    arcs = []
    for a in t["arcs"]:
        pts = np.cumsum(np.array(a, dtype=float), axis=0)
        arcs.append(np.column_stack([pts[:, 0] * sc[0] + tr[0], pts[:, 1] * sc[1] + tr[1]]))
    def ring(idx):
        out = []
        for i in idx:
            seg = arcs[i] if i >= 0 else arcs[~i][::-1]
            out.append(seg if not out else seg[1:])
        return np.vstack(out)
    res = {}
    for g in t["objects"][obj]["geometries"]:
        if g.get("type") is None:
            continue
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
        res[g["properties"]["name"]] = [ring(r) for p in polys for r in p]
    return res


def centroid(rings):
    """Area-weighted centroid of the largest ring, in lon/lat."""
    best, ba = None, -1
    for r in rings:
        x, y = r[:, 0], r[:, 1]
        a = 0.5 * np.sum(x[:-1] * y[1:] - x[1:] * y[:-1])
        if abs(a) > ba and abs(a) > 0:
            cx = np.sum((x[:-1] + x[1:]) * (x[:-1] * y[1:] - x[1:] * y[:-1])) / (6 * a)
            cy = np.sum((y[:-1] + y[1:]) * (x[:-1] * y[1:] - x[1:] * y[:-1])) / (6 * a)
            best, ba = (cx, cy), abs(a)
    return best


def equal_earth(lon, lat):
    A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
    th = np.arcsin(math.sqrt(3) / 2 * np.sin(np.radians(lat)))
    x = 2 * math.sqrt(3) * np.radians(lon) * np.cos(th) / (3 * (9 * A4 * th**8 + 7 * A3 * th**6 + 3 * A2 * th**2 + A1))
    y = A4 * th**9 + A3 * th**7 + A2 * th**3 + A1 * th
    return x, y


def albers(lon, lat, lat1=29.5, lat2=45.5, lat0=37.5, lon0=-96.0):
    p1, p2, p0 = map(math.radians, (lat1, lat2, lat0))
    n = (math.sin(p1) + math.sin(p2)) / 2
    C = math.cos(p1) ** 2 + 2 * n * math.sin(p1)
    rho0 = math.sqrt(C - 2 * n * math.sin(p0)) / n
    rho = np.sqrt(C - 2 * n * np.sin(np.radians(lat))) / n
    th = n * np.radians(lon - lon0)
    return rho * np.sin(th), rho0 - rho * np.cos(th)


def add_poly(ax, rings, proj, **kw):
    verts, codes = [], []
    for r in rings:
        lon = r[:, 0].copy()
        if lon.max() - lon.min() > 300:          # ring crosses the antimeridian: keep it on the eastern edge
            lon[lon < 0] = 180.0
        x, y = proj(lon, r[:, 1])
        verts += list(zip(x, y))
        codes += [Path.MOVETO] + [Path.LINETO] * (len(r) - 2) + [Path.CLOSEPOLY]
    ax.add_patch(PathPatch(Path(verts, codes), **kw))


K = 13 / math.sqrt(385.3)                      # bubble radius in points per sqrt($M); Canada is 13 pt
def rad(v):
    return K * math.sqrt(max(v, 0.05))
def usd(v):
    return f"\\${v / 1000:.1f}B" if v >= 1000 else f"\\${v:.0f}M"


world = topo(f"{ATLAS}/world-atlas/countries-110m.json", "countries")
states = topo(f"{ATLAS}/us-atlas/states-10m.json", "states")
exp = [(r["country"], float(r["value_usd"]) / 1e6) for r in csv.DictReader(open(os.path.join(HERE, "2024_maine-wood-exports-by-country_DATA.csv")))]
cfs = list(csv.DictReader(open(os.path.join(HERE, "2022_maine-net-shipments-to-states-cfs_DATA.csv"))))
total_exp = 385.287058 / 0.6673                # total exports, from Canada's value and share in the source file
net_pos = sum(float(r["net_musd"]) for r in cfs if float(r["net_musd"]) > 0)

alias = {"Dominican Republic": "Dominican Rep.", "Korea, South": "South Korea"}
fixed = {"Hong Kong": (114.17, 22.3), "Singapore": (103.8, 1.35), "Seychelles": (55.5, -4.7), "Canada": (-79.0, 53.0),
         "Indonesia": (113.0, -1.0), "Chile": (-71.0, -33.0)}
MAINE = (-69.2, 45.3)

fig = plt.figure(figsize=(10, 8.6), dpi=300)
fig.patch.set_facecolor("white")
fig.text(0.04, 0.955, "Maine's wood mostly stays in the U.S., and most exports go to Canada", fontfamily="Liberation Serif",
         fontweight="bold", fontsize=19.5, color=GRN, ha="left", va="center")
fig.text(0.04, 0.917, f"Other states took about {usd(net_pos)} more of Maine's wood, pulp, and paper than they sent back in 2022. "
         f"Exports abroad were {usd(total_exp)} in 2024,\nand Canada took 67% of them. Circle area is the dollar value on one scale for both maps.",
         fontsize=10.2, color=INK, ha="left", va="center", linespacing=1.3)

# ---- world map ----
ax = fig.add_axes([0.02, 0.36, 0.96, 0.52])
ax.set_axis_off(); ax.set_aspect("equal")
for name, rings in world.items():
    if name == "Antarctica":
        continue
    add_poly(ax, rings, equal_earth, facecolor="#BFD3E3" if name == "United States of America" else LAND, edgecolor="white", linewidth=0.35, zorder=1)
x0, _ = equal_earth(np.array([-170.0]), np.array([0.0])); x1, _ = equal_earth(np.array([180.0]), np.array([0.0]))
_, y0 = equal_earth(np.array([0.0]), np.array([-58.0])); _, y1 = equal_earth(np.array([0.0]), np.array([80.0]))
ax.set_xlim(x0[0], x1[0]); ax.set_ylim(y0[0], y1[0])
mx, my = equal_earth(np.array([MAINE[0]]), np.array([MAINE[1]]))
pts = []
for c, v in exp:
    lon, lat = fixed.get(c) or centroid(world[alias.get(c, c)])
    x, y = equal_earth(np.array([lon]), np.array([lat]))
    pts.append((c, v, x[0], y[0]))
lab = {"Canada": (-16, 12, "right"), "China": (9, -9, "left"), "Belgium": (-7, 9, "right"), "Italy": (8, -8, "left"),
       "Germany": (7, 9, "left"), "Mexico": (-8, -2, "right"), "Costa Rica": (-6, -6, "right"), "Brazil": (6, -5, "left"),
       "Colombia": (6, 0, "left"), "Dominican Republic": (7, 5, "left"), "Uzbekistan": (0, 8, "center"), "Indonesia": (0, -9, "center")}
for c, v, x, y in sorted(pts, key=lambda p: -p[1]):
    if c in lab:
        ax.plot([mx[0], x], [my[0], y], color=ORG, lw=0.5 + 2.2 * math.sqrt(v / 385.3), alpha=0.35, zorder=2, solid_capstyle="round")
    ax.scatter([x], [y], s=(2 * rad(v)) ** 2, c=ORG, edgecolors="white", linewidths=0.6, zorder=3, alpha=0.93)
    if c in lab:
        dx, dy, ha = lab[c]
        ax.annotate(f"{c} {usd(v)}", (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center", fontsize=8.8, fontweight="bold", color=INK, path_effects=halo, zorder=5)
ax.scatter(mx, my, s=42, c=GRN, edgecolors="white", linewidths=1.0, zorder=6)
ax.text(mx[0] + 0.08, my[0] - 0.02, "MAINE", ha="left", va="center", fontsize=9.2, fontweight="bold", color=GRN, path_effects=halo, zorder=6)
ax.text(0.0, 0.30, "EXPORTS BY COUNTRY, 2024", transform=ax.transAxes, ha="left", va="bottom", fontsize=9.6, fontweight="bold", color=INK)

# ---- U.S. inset ----
bx = fig.add_axes([0.03, 0.035, 0.56, 0.315])
bx.set_axis_off(); bx.set_aspect("equal")
skip = {"Alaska", "Hawaii", "Puerto Rico", "Guam", "American Samoa", "United States Virgin Islands", "Commonwealth of the Northern Mariana Islands"}
for name, rings in states.items():
    if name in skip:
        continue
    add_poly(bx, rings, albers, facecolor="#BFD3E3" if name == "Maine" else LAND, edgecolor="white", linewidth=0.45, zorder=1)
bx.set_xlim(-0.40, 0.42); bx.set_ylim(-0.235, 0.25)
slab = {"New York": (-4, 22, "right"), "Indiana": (-10, -12, "right"), "North Carolina": (11, -9, "left"),
        "Wisconsin": (-12, 9, "right"), "Georgia": (9, -9, "left"), "Texas": (0, -11, "center"), "New Hampshire": (14, 10, "left"), "Massachusetts": (13, -3, "left")}
for r in sorted(cfs, key=lambda r: -abs(float(r["net_musd"]))):
    net, low = float(r["net_musd"]), r["low_confidence"] == "TRUE"
    lon, lat = centroid(states[r["state"]])
    x, y = albers(np.array([lon]), np.array([lat]))
    col = ORG if net > 0 else NAV
    bx.scatter(x, y, s=(2 * rad(abs(net))) ** 2, facecolors="white" if low else col, edgecolors=col, linewidths=1.5 if low else 0.6, zorder=3, alpha=0.93)
    if r["state"] in slab:
        dx, dy, ha = slab[r["state"]]
        txt = f"{r['state']} {usd(net)}" if net > 0 else f"{r['state']} sends Maine {usd(-net)} more"
        bx.annotate(txt, (x[0], y[0]), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center", fontsize=8.4, fontweight="bold", color=INK, path_effects=halo, zorder=5)
fig.text(0.04, 0.345, "NET SHIPMENTS TO OTHER STATES, 2022", ha="left", va="center", fontsize=9.6, fontweight="bold", color=INK)

# ---- key and notes ----
kx = fig.add_axes([0.60, 0.035, 0.38, 0.315]); kx.set_axis_off(); kx.set_xlim(0, 1); kx.set_ylim(0, 1)
kx.text(0.0, 0.93, "HOW TO READ IT", fontsize=9.6, fontweight="bold", color=INK, va="center")
xs = [0.07, 0.22, 0.44, 0.76]
for xk, v in zip(xs, (5, 50, 385, 1265)):
    kx.scatter([xk], [0.70], s=(2 * rad(v)) ** 2, c=ORG, edgecolors="white", linewidths=0.6, clip_on=False)
    kx.text(xk, 0.47, usd(v), ha="center", va="center", fontsize=9.2, fontweight="bold", color=INK)
notes = [(ORG, True, "takes more from Maine than it sends"), (NAV, True, "sends Maine more than it takes"),
         (ORG, False, "open circle: survey uncertainty above 30%")]
for i, (col, filled, t) in enumerate(notes):
    yk = 0.30 - 0.075 * i
    kx.scatter([0.03], [yk], s=42, facecolors=col if filled else "white", edgecolors=col, linewidths=1.4, clip_on=False)
    kx.text(0.075, yk, t, fontsize=8.8, color=INK, va="center")
kx.text(0.0, -0.02, "State figures are floors because the survey\nwithholds some cells.", fontsize=8.4, color=GRY, va="bottom", linespacing=1.25)

fig.savefig(OUT, dpi=300, facecolor="white")
print("saved", OUT, round(net_pos), round(total_exp))
