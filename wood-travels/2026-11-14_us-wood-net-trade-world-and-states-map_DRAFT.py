# U.S. net wood trade by world region, and each state's net wood trade (other states plus abroad), 2024.
# Built November 14, 2026, as a companion to the Maine net trade map.
# Inputs (same folder), Freight Analysis Framework version 5.6.1 data tabulation tool (BTS and FHWA), SCTG 25 to 28, current dollars, 2024 estimates:
#   2024_us-wood-trade-by-world-region-faf5_DATA.csv   2024_us-wood-trade-by-state-faf5_DATA.csv
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



K = 21 / math.sqrt(11244)                       # bubble radius in points per sqrt($M); Canada (-$11.2B) is 21 pt
def rad(v):
    return K * math.sqrt(max(v, 1))
def usd(v):
    return f"\\${v / 1000:.1f}B" if v >= 1000 else f"\\${v:.0f}M"

world = topo(f"{ATLAS}/world-atlas/countries-110m.json", "countries")
states = topo(f"{ATLAS}/us-atlas/states-10m.json", "states")
rd = lambda f: list(csv.DictReader(open(os.path.join(HERE, f))))
reg = {r["region"]: (float(r["import_musd"]), float(r["export_musd"])) for r in rd("2024_us-wood-trade-by-world-region-faf5_DATA.csv")}
st = {}
for r in rd("2024_us-wood-trade-by-state-faf5_DATA.csv"):
    o = float(r["dom_out_musd"]) + float(r["export_musd"]); i = float(r["dom_in_musd"]) + float(r["import_musd"]); st[r["state"]] = (o - i, o / i)
imp = sum(v[0] for v in reg.values()); exp_ = sum(v[1] for v in reg.values())
nsell = sum(1 for k, v in st.items() if v[0] > 0 and k != "Washington DC")
print("US imports", imp, "exports", exp_, "net", exp_ - imp, "net-selling states", nsell, "Maine", st["Maine"])

pos = {"Canada": (-100.0, 57.0), "Mexico": (-102.0, 23.5), "Rest of Americas": (-58.0, -12.0), "Europe": (12.0, 50.0), "Africa": (20.0, 5.0),
       "SW & Central Asia": (62.0, 30.0), "Eastern Asia": (112.0, 35.0), "SE Asia & Oceania": (128.0, -12.0)}
nice = {"Rest of Americas": "Rest of the Americas", "SW & Central Asia": "Southwest and Central Asia", "SE Asia & Oceania": "Southeast Asia and Oceania"}
US = (-96.0, 39.0)

fig = plt.figure(figsize=(10, 8.6), dpi=300)
fig.patch.set_facecolor("white")
fig.text(0.04, 0.955, "The U.S. buys more wood than it sells. Maine does the reverse", fontweight="bold", fontsize=18, color="#1A1A1A", ha="left", va="center")
fig.text(0.04, 0.917, f"In 2024 the U.S. bought {usd(imp - exp_)} more wood, pulp, and paper abroad than it sold, most of it from Canada. Maine is one of {nsell} states\n"
         f"that ship out more than they take in, and it sells about {st['Maine'][1]:.0f} times what it buys. Circle area is the net dollar value.",
         fontsize=10.2, color=INK, ha="left", va="center", linespacing=1.3)

ax = fig.add_axes([0.02, 0.36, 0.96, 0.52])
ax.set_axis_off(); ax.set_aspect("equal")
for name, rings in world.items():
    if name == "Antarctica":
        continue
    add_poly(ax, rings, equal_earth, facecolor="#BFD3E3" if name == "United States of America" else LAND, edgecolor="white", linewidth=0.35, zorder=1)
x0, _ = equal_earth(np.array([-170.0]), np.array([0.0])); x1, _ = equal_earth(np.array([180.0]), np.array([0.0]))
_, y0 = equal_earth(np.array([0.0]), np.array([-58.0])); _, y1 = equal_earth(np.array([0.0]), np.array([80.0]))
ax.set_xlim(x0[0], x1[0]); ax.set_ylim(y0[0], y1[0])
mx, my = equal_earth(np.array([US[0]]), np.array([US[1]]))
lab = {"Canada": (28, 24, "left"), "Mexico": (-12, -6, "right"), "Rest of the Americas": (14, -4, "left"), "Europe": (14, -1, "left"), "Africa": (8, -6, "left"),
       "Southwest and Central Asia": (0, -17, "center"), "Eastern Asia": (0, 16, "center"), "Southeast Asia and Oceania": (0, -19, "center")}
for k, (i, o) in sorted(reg.items(), key=lambda t: -abs(t[1][1] - t[1][0])):
    net = o - i; name = nice.get(k, k)
    x, y = equal_earth(np.array([pos[k][0]]), np.array([pos[k][1]])); x, y = x[0], y[0]
    col = ORG if net > 0 else NAV
    ax.plot([mx[0], x], [my[0], y], color=col, lw=0.5 + 2.6 * math.sqrt(abs(net) / 11244), alpha=0.35, zorder=2, solid_capstyle="round")
    ax.scatter([x], [y], s=(2 * rad(abs(net))) ** 2, c=col, edgecolors=col, linewidths=0.8, zorder=3, alpha=0.55)
    dx, dy, ha = lab[name]
    txt = f"{name} +{usd(net)}" if net > 0 else f"{name}: sells the U.S. {usd(-net)} more"
    ax.annotate(txt, (x, y), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center", fontsize=8.6, fontweight="bold", color=INK, path_effects=halo, zorder=5)
ax.text(0.0, 0.30, "U.S. NET TRADE BY WORLD REGION, 2024", transform=ax.transAxes, ha="left", va="bottom", fontsize=9.6, fontweight="bold", color=INK)

bx = fig.add_axes([0.03, 0.035, 0.56, 0.315])
bx.set_axis_off(); bx.set_aspect("equal")
skip = {"Alaska", "Hawaii", "Puerto Rico", "Guam", "American Samoa", "United States Virgin Islands", "Commonwealth of the Northern Mariana Islands"}
for name, rings in states.items():
    if name in skip:
        continue
    add_poly(bx, rings, albers, facecolor="#BFD3E3" if name == "Maine" else LAND, edgecolor="white", linewidth=0.45, zorder=1)
bx.set_xlim(-0.40, 0.42); bx.set_ylim(-0.235, 0.25)
slab = {"Maine": (16, 10, "left"), "Oregon": (16, 14, "left"), "Alabama": (4, -22, "center"), "Arkansas": (-16, 4, "right"), "California": (14, -18, "left"),
        "Texas": (0, -24, "center"), "Florida": (20, 2, "left")}
for s, (net, ratio) in sorted(st.items(), key=lambda t: -abs(t[1][0])):
    if s in ("Alaska", "Hawaii", "Washington DC"):
        continue
    lon, lat = centroid(states[s])
    x, y = albers(np.array([lon]), np.array([lat]))
    col = ORG if net > 0 else NAV
    bx.scatter(x, y, s=(2 * rad(abs(net))) ** 2, facecolors=col, edgecolors=GRN if s == "Maine" else col, linewidths=2.0 if s == "Maine" else 0.8, zorder=4 if s == "Maine" else 3, alpha=0.9 if s == "Maine" else 0.55)
    if s in slab:
        dx, dy, ha = slab[s]
        txt = f"{s} +{usd(net)}" if net > 0 else f"{s} −{usd(-net)}"
        bx.annotate(txt, (x[0], y[0]), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center", fontsize=8.4, fontweight="bold", color=GRN if s == "Maine" else INK, path_effects=halo, zorder=5)
fig.text(0.04, 0.345, "EACH STATE'S NET WOOD TRADE, 2024", ha="left", va="center", fontsize=9.6, fontweight="bold", color=INK)

kx = fig.add_axes([0.60, 0.035, 0.38, 0.315]); kx.set_axis_off(); kx.set_xlim(0, 1); kx.set_ylim(0, 1)
kx.text(0.0, 0.93, "HOW TO READ IT", fontsize=9.6, fontweight="bold", color=INK, va="center")
for xk, v in zip([0.08, 0.30, 0.66], (1000, 5000, 15000)):
    kx.scatter([xk], [0.70], s=(2 * rad(v)) ** 2, c=ORG, edgecolors=ORG, linewidths=0.8, alpha=0.55, clip_on=False)
    kx.text(xk, 0.44, usd(v), ha="center", va="center", fontsize=9.2, fontweight="bold", color=INK)
for i, (col, t) in enumerate([(ORG, "sells more wood than it buys"), (NAV, "buys more wood than it sells")]):
    yk = 0.30 - 0.075 * i
    kx.scatter([0.03], [yk], s=42, facecolors=col, edgecolors=col, linewidths=1.4, clip_on=False)
    kx.text(0.075, yk, t, fontsize=8.8, color=INK, va="center")
kx.text(0.0, -0.02, "Logs, wood products, pulp, and paper. State circles\ncount trade with other states and abroad. Figures\nare modeled federal freight estimates.", fontsize=8.4, color=GRY, va="bottom", linespacing=1.25)
fig.savefig(OUT, dpi=300, facecolor="white"); print("saved", OUT)
