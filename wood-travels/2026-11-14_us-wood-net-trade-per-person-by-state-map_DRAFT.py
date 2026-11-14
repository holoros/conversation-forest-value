# Net wood trade per person by state, 2024: all wood, then wood products and pulp and paper separately, with a ranked comparison.
# Built November 14, 2026. It replaces the bubble version (2026-11-14_us-wood-net-trade-world-and-states-map_DRAFT), which is kept.
# Inputs (same folder):
#   2024_us-wood-trade-by-state-and-commodity-faf5_DATA.csv   Freight Analysis Framework 5.6.1 data tabulation tool, SCTG 25 to 28, current $M, 2024
#       columns o = shipped to other states, i = received from other states, x = exports, m = imports, by SCTG code
#   2025_state-population-census-vintage-2025_DATA.csv        U.S. Census Bureau July 1, 2025 estimates (transcribed from Wikipedia's state table)
# Net per person = (o + x - i - m) / population. Usage: python3 <script> <node_modules dir with us-atlas> <out.png>
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



from matplotlib.patches import Rectangle
states = topo(f"{ATLAS}/us-atlas/states-10m.json", "states")
rd = lambda f: list(csv.DictReader(open(os.path.join(HERE, f))))
pop = {r["state"]: int(r["population_july_1_2025"]) for r in rd("2025_state-population-census-vintage-2025_DATA.csv")}
val = {}
for r in rd("2024_us-wood-trade-by-state-and-commodity-faf5_DATA.csv"):
    g = lambda k: float(r[k]); s = r["state"]
    wood = sum(g("o" + c) + g("x" + c) - g("i" + c) - g("m" + c) for c in ("25", "26"))
    paper = sum(g("o" + c) + g("x" + c) - g("i" + c) - g("m" + c) for c in ("27", "28"))
    val[s] = tuple(v * 1e6 / pop[s] for v in (wood + paper, wood, paper))
us_pp = sum((float(r["x" + c]) - float(r["m" + c])) for r in rd("2024_us-wood-trade-by-state-and-commodity-faf5_DATA.csv") for c in ("25", "26", "27", "28")) * 1e6 / sum(pop.values())
rank = sorted(val, key=lambda s: -val[s][0])
print("Maine", [round(v) for v in val["Maine"]], "rank", rank.index("Maine") + 1, "| Massachusetts", [round(v) for v in val["Massachusetts"]], "| US abroad per person", round(us_pp), "| top", rank[:5])

EDGES = [-500, -100, 100, 500, 1500]
COLS = ["#2B5C8A", "#8FB3D3", "#ECE9E2", "#F3C4A2", "#E08A4F", "#B4451A"]            # buys more ... sells more
LABS = ["buys \\$500+ more", "buys \\$100 to \\$500 more", "about even", "sells \\$100 to \\$500 more", "sells \\$500 to \\$1,500 more", "sells \\$1,500+ more"]
def cls(v):
    return sum(v >= e for e in EDGES)
def money(v):
    return ("+" if v >= 0 else "\u2212") + f"\\${round(abs(v), -1):,.0f}"
skip = {"Alaska", "Hawaii", "Puerto Rico", "Guam", "American Samoa", "United States Virgin Islands", "Commonwealth of the Northern Mariana Islands"}
key = {"District of Columbia": "Washington DC"}

def draw(ax, k, labels=None, lw=0.5):
    ax.set_axis_off(); ax.set_aspect("equal")
    for name, rings in states.items():
        if name in skip:
            continue
        v = val[key.get(name, name)][k]
        add_poly(ax, rings, albers, facecolor=COLS[cls(v)], edgecolor="#1F4D36" if name == "Maine" else "white", linewidth=1.6 if name == "Maine" else lw, zorder=3 if name == "Maine" else 1)
    ax.set_xlim(-0.395, 0.405); ax.set_ylim(-0.235, 0.245)
    for name, (dx, dy, ha) in (labels or {}).items():
        lon, lat = centroid(states[name]); x, y = albers(np.array([lon]), np.array([lat]))
        if ha == "in":
            ax.text(x[0], y[0], f"{name}\n{money(val[name][k])}", ha="center", va="center", fontsize=9.2, fontweight="bold", color="white", linespacing=1.1, zorder=6)
            continue
        sep = "\n" if ha == "right2" else " "; ha = "right" if ha == "right2" else ha
        ax.annotate(f"{name}{sep}{money(val[name][k])}", (x[0], y[0]), xytext=(dx, dy), textcoords="offset points", ha=ha, linespacing=1.1, va="center", fontsize=9.2, fontweight="bold",
                    color=INK, path_effects=halo, zorder=6, arrowprops=dict(arrowstyle="-", color=INK, lw=0.7, shrinkA=0, shrinkB=1) if abs(dx) + abs(dy) > 26 else None)

fig = plt.figure(figsize=(10, 8.6), dpi=300); fig.patch.set_facecolor("white")
fig.text(0.04, 0.957, "Per person, Maine ships out more wood and paper on net than any other state", fontweight="bold", fontsize=17, color="#1A1A1A", ha="left", va="center")
fig.text(0.04, 0.917, f"In 2024 Maine shipped out about \\${round(val['Maine'][0], -1):,.0f} more wood, pulp, and paper per resident than it brought in, federal estimates show, narrowly\n"
         f"ahead of Oregon. Massachusetts brought in about \\${round(-val['Massachusetts'][0], -1):,.0f} more per resident than it shipped out, and New Hampshire about \\${round(-val['New Hampshire'][0], -1):,.0f} more.", fontsize=10.6, color=INK, ha="left", va="center", linespacing=1.3)

a = fig.add_axes([0.02, 0.395, 0.60, 0.455])
draw(a, 0, {"Maine": (26, 20, "left"), "Oregon": (0, 0, "in"), "Arkansas": (-74, -4, "right"), "Massachusetts": (14, -50, "left"), "California": (16, -72, "center"), "Texas": (-18, -62, "center")})
fig.text(0.04, 0.868, "ALL WOOD, PULP, AND PAPER: SHIPPED OUT MINUS BROUGHT IN, PER RESIDENT", fontsize=10, fontweight="bold", color=INK, ha="left", va="center")
lx = fig.add_axes([0.04, 0.368, 0.56, 0.03]); lx.set_axis_off(); lx.set_xlim(0, 6); lx.set_ylim(0, 1)
for i, (c, t) in enumerate(zip(COLS, ["brings in\n\\$500+ more", "brings in \\$100\nto \\$500 more", "within \\$100\neither way", "ships out \\$100\nto \\$500 more", "ships out \\$500\nto \\$1,500 more", "ships out\n\\$1,500+ more"])):
    lx.add_patch(Rectangle((i, 0.45), 1, 0.55, facecolor=c, edgecolor="white", lw=0.8))
    lx.text(i + 0.5, 0.30, t, ha="center", va="top", fontsize=9, color=INK, linespacing=1.1)

b = fig.add_axes([0.715, 0.375, 0.255, 0.455])
grp = rank[:5] + ["Vermont", "Connecticut", "Rhode Island", "Massachusetts", "New York", "New Hampshire"]
ys = list(range(len(grp)))[::-1]; ys = [y + (0.7 if i < 5 else 0) for i, y in enumerate(ys)]
for s, y in zip(grp, ys):
    v = val[s][0]
    b.barh(y, v, height=0.66, color=COLS[cls(v)], edgecolor="#1F4D36" if s == "Maine" else "#9A9A9A", linewidth=1.4 if s == "Maine" else 0.6)
    b.text(-70 if v >= 0 else 70, y, s, ha="right" if v >= 0 else "left", va="center", fontsize=9.4, fontweight="bold", color="#1F4D36" if s == "Maine" else INK)
    b.text(v + (45 if v >= 0 else -45), y, money(v), ha="left" if v >= 0 else "right", va="center", fontsize=9.2, fontweight="bold", color=INK)
b.plot([0, 0], [ys[4] - 0.45, ys[0] + 0.45], color=INK, lw=0.9); b.plot([0, 0], [-0.5, ys[5] + 0.45], color=INK, lw=0.9); b.set_xlim(-1750, 3300); b.set_ylim(-0.7, len(grp) + 0.4); b.set_axis_off()
b.text(-1750, ys[0] + 0.78, "TOP FIVE NET SHIPPERS", fontsize=9.4, fontweight="bold", color=GRY, ha="left", va="center")
b.text(-1750, ys[5] + 0.72, "NEW ENGLAND AND NEW YORK", fontsize=9.4, fontweight="bold", color=GRY, ha="left", va="center")
fig.text(0.715, 0.868, "NET DOLLARS PER RESIDENT", fontsize=10, fontweight="bold", color=INK, ha="left", va="center")

for j, (k, title, labs) in enumerate([(1, "LOGS, LUMBER, AND PANELS", {"Maine": (20, 10, "left"), "Oregon": (-34, -30, "right2")}), (2, "PULP AND PAPER", {"Maine": (20, 14, "left"), "Louisiana": (-2, -30, "center")})]):
    c = fig.add_axes([0.02 + 0.49 * j, 0.068, 0.47, 0.222]); draw(c, k, labs, lw=0.4)
    fig.text(0.04 + 0.49 * j, 0.300, title + ", PER RESIDENT (SAME COLORS)", fontsize=10, fontweight="bold", color=INK, ha="left", va="center")
fig.text(0.04, 0.030, "Counts shipments to and from other states and countries, including goods passing through warehouses and ports, not what residents use. The estimates\nundercount raw logs crossing the Canadian border, so small gaps between states are uncertain. Alaska and Hawaii, which bring in more than they ship out, are\nnot shown. Modeled estimates from the federal Freight Analysis Framework (2024) and Census Bureau population (2025). Furniture is not included. Center for Research on Sustainable Forests, University of Maine.", fontsize=9, color=GRY, ha="left", va="center", linespacing=1.3)
fig.savefig(OUT, dpi=300, facecolor="white"); print("saved", OUT)
