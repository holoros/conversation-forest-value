# Follow the wood with a leakage layer. Rebuilt November 12, 2026 (second pass: Equal Earth projection so
# shapes are not stretched, pulp trade arrows scaled by tonnage, sans headline to match The Conversation's charts).
# Shading: colors read from figure 2a of Daigneault et al. 2025 (Environ. Res. Lett. 20:114022, CC BY 4.0;
# `2025_daigneault-erl-fig2a-leakage-layer_DATA.png`) and assigned to each Global Timber Model region and forest
# type code on Adam Daigneault's 0.5 degree forest type grid (not in this repository; pass its CSV with X, Y, code).
# Each code takes the most common figure color among its cells. No leakage value is computed here.
# Pulp arrows: UN Comtrade, U.S.-reported trade, 2024. Imports are bleached kraft pulp (HS 470321 softwood and
# 470329 hardwood): Brazil 0.266 + 2.024 = 2.29 million metric tons, Canada 1.729 + 0.110 = 1.84 million.
# Exports are all kraft pulp (HS 4703): 0.08 million to Brazil, 0.50 million to Canada.
# Routes are schematic. Usage: python3 <script> <node_modules dir> <grid.csv> <out.png>
import csv, json, sys, os, math, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, FancyArrowPatch
from matplotlib.collections import PolyCollection
from matplotlib.path import Path
import matplotlib.patheffects as pe
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ATLAS, GRID, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
plt.rcParams["font.family"] = "Liberation Sans"
plt.rcParams["mathtext.fontset"] = "custom"; plt.rcParams["mathtext.bf"] = "Liberation Sans:bold"; plt.rcParams["mathtext.rm"] = "Liberation Sans"
GRN, NAV, LAND, SEA, INK, GRY = "#1F4D36", "#12355B", "#E8E6E1", "#F4F8FB", "#1A1A1A", "#5F6B65"
LON0 = -72.0
LX0, LX1, LY0, LY1 = -124.0, -27.0, -35.0, 53.5          # frame in degrees


def ee(lon, lat):
    A1, A2, A3, A4 = 1.340264, -0.081106, 0.000893, 0.003796
    lon, lat = np.asarray(lon, float), np.asarray(lat, float)
    th = np.arcsin(math.sqrt(3) / 2 * np.sin(np.radians(lat)))
    x = 2 * math.sqrt(3) * np.radians(lon - LON0) * np.cos(th) / (3 * (9 * A4 * th**8 + 7 * A3 * th**6 + 3 * A2 * th**2 + A1))
    return x, A4 * th**9 + A3 * th**7 + A2 * th**3 + A1 * th


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
        res.setdefault(g["properties"]["name"], []).extend(ring(r) for p in polys for r in p)
    return res


def near(r):
    return not (r[:, 0].max() < LX0 - 25 or r[:, 0].min() > LX1 + 12 or r[:, 1].max() < LY0 - 8 or r[:, 1].min() > LY1 + 12
                or r[:, 0].max() - r[:, 0].min() > 300)


def path_of(rings):
    verts, codes = [], []
    for r in rings:
        if not near(r):
            continue
        x, y = ee(r[:, 0], r[:, 1])
        verts += list(zip(x, y)); codes += [Path.MOVETO] + [Path.LINETO] * (len(r) - 2) + [Path.CLOSEPOLY]
    return Path(verts, codes) if verts else None


# ---- leakage colors by forest type code ----
lay = np.array(Image.open(os.path.join(HERE, "2025_daigneault-erl-fig2a-leakage-layer_DATA.png")).convert("RGB")).astype(int)
SC, FX0 = 3.745, -177.5
FYMX = 314.7 / SC
rows = [(float(r["X"]), float(r["Y"]), int(r["code"])) for r in csv.DictReader(open(GRID))]
votes = collections.defaultdict(collections.Counter)
for x, y, c in rows:
    px, py = int(round((x - FX0) * SC)), int(round((FYMX - y) * SC))
    if 0 <= px < lay.shape[1] and 0 <= py < lay.shape[0]:
        r, g, b = lay[py, px]
        if max(r, g, b) - min(r, g, b) > 95 and r > 190:      # a leakage color, not gray land, white sea or text
            votes[c][(r // 8 * 8, g // 8 * 8, b // 8 * 8)] += 1
def pick(v):
    """Most saturated color among those holding at least 15% of a code's cells (drops blended edge pixels)."""
    n = sum(v.values())
    cand = [k for k, m in v.items() if m >= 0.15 * n] or [v.most_common(1)[0][0]]
    return max(cand, key=lambda k: (max(k) - min(k), v[k]))
colr = {c: np.array(pick(v)) / 255.0 for c, v in votes.items() if sum(v.values()) >= 3}
d = 0.499306 / 2
polys, cols = [], []
for x, y, c in rows:
    if c in colr and LX0 - 20 <= x <= LX1 + 8 and LY0 - 6 <= y <= LY1 + 8:
        px, py = ee([x - d, x + d, x + d, x - d], [y - d, y - d, y + d, y + d])
        polys.append(list(zip(px, py))); cols.append(colr[c])
print("cells drawn", len(polys), "codes colored", len(colr))

x0, _ = ee(LX0, 10); x1, _ = ee(LX1, 10); _, y0 = ee(LON0, LY0); _, y1 = ee(LON0, LY1)
W = 10.0; axw = 0.94; axh_in = W * axw * (y1 - y0) / (x1 - x0); H = axh_in + 1.5
fig = plt.figure(figsize=(W, H), dpi=300)
ax = fig.add_axes([0.03, 0.15 / H, axw, axh_in / H])
ax.set_xlim(x0, x1); ax.set_ylim(y0, y1); ax.set_aspect("equal"); ax.set_axis_off()
ax.add_patch(plt.Rectangle((x0, y0), x1 - x0, y1 - y0, facecolor=SEA, edgecolor="none", zorder=0))
world = topo(f"{ATLAS}/world-atlas/countries-50m.json", "countries")
states = topo(f"{ATLAS}/us-atlas/states-10m.json", "states")
land = path_of([r for rings in world.values() for r in rings])
ax.add_patch(PathPatch(land, facecolor=LAND, edgecolor="none", zorder=1))
pc = PolyCollection(polys, facecolors=cols, edgecolors=cols, linewidths=0.15, zorder=2)
ax.add_collection(pc); pc.set_clip_path(PathPatch(land, transform=ax.transData))
ax.add_patch(PathPatch(land, facecolor="none", edgecolor="white", linewidth=0.5, zorder=3))
for name, rings in states.items():
    p = path_of(rings)
    if p is not None:
        ax.add_patch(PathPatch(p, facecolor="none", edgecolor="white", linewidth=0.35, zorder=3))
ax.add_patch(PathPatch(path_of(states["Maine"]), facecolor="none", edgecolor="#0B2A1B", linewidth=1.8, zorder=5))

P = lambda lon, lat: tuple(float(v) for v in ee(lon, lat))
halo = [pe.withStroke(linewidth=3, foreground="white")]
def route(pts, lw, color=NAV, ls="-", head=(9, 5)):
    path = Path([P(*p) for p in pts], [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4])
    ax.add_patch(FancyArrowPatch(path=path, arrowstyle=f"-|>,head_length={head[0]},head_width={head[1]}", color=color,
                                 linewidth=lw, linestyle=ls, zorder=6, capstyle="round"))
K = 6.6 / 2.29                                               # line width in points per million metric tons
SJ, MAC, BR = (-66.06, 45.27), (-83.63, 32.84), (-51.7, -20.8)
route([BR, (-31.0, -22.0), (-50.0, 22.0), (-78.9, 33.4)], K * 2.29, head=(11, 7))          # Brazil to U.S. ports
route([(-79.5, 49.5), (-83.5, 47.5), (-86.5, 44.0), (-86.0, 40.3)], K * 1.84, head=(10, 6))  # Canada to U.S. mills
route([SJ, (-60.0, 39.5), (-70.0, 28.0), (MAC[0] + 0.9, MAC[1] - 0.3)], 1.5, ls=(0, (4, 2.5)), head=(7, 4))
for p in (SJ, MAC, BR):
    ax.scatter(*P(*p), s=60, c=INK, edgecolors="white", linewidths=0.8, zorder=7)

box = dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=INK, linewidth=0.6)
def lab(lon, lat, t, ha="center", va="center", fs=10.4):
    ax.text(*P(lon, lat), t, ha=ha, va=va, fontsize=fs, color=INK, bbox=box, zorder=8, linespacing=1.2)
def tag(lon, lat, big, small, ha="center"):
    ax.text(*P(lon, lat), r"$\bf{" + big.replace(" ", r"\ ") + "}$\n" + small, ha=ha, va="center", fontsize=10.4, color=INK, bbox=box, zorder=8, linespacing=1.25)
tag(-40.5, 13.0, "2.3M metric tons of pulp", "from Brazil to the U.S. in 2024;\n0.1M went the other way")
tag(-103.0, 47.0, "1.8M metric tons of pulp", "from Canada to the U.S. in 2024;\n0.5M went the other way")
lab(-62.2, 49.4, "Saint John, N.B.\npulp mill", ha="left")
lab(-97.5, 27.0, "Macon, Ga.\nSaint John pulp\nbecomes tissue")
ax.plot(*zip(P(-56.0, 36.4), P(-68.4, 44.7)), color=GRY, linewidth=0.7, zorder=6)
lab(-46.5, 32.0, "Maine logs cross the border to Quebec\nsawmills. In 2023, about 2 million tons of\nMaine's harvest left the state unprocessed,\nwhile 2.7 million tons came in from\nneighboring states and provinces")
lab(-44.5, -31.2, "Brazil supplies about 82% of\nthe hardwood pulp the U.S. imports,\nmostly from eucalyptus plantations")
ax.text(*P(-69.2, 48.7), "MAINE", ha="center", va="center", fontsize=11, fontweight="bold", color=GRN, zorder=8, path_effects=halo)

# ---- legend ----
bar = np.array(Image.open(os.path.join(HERE, "2025_daigneault-erl-fig2-legend-bar_DATA.png")).convert("RGB"))
bx0, by0 = P(-119.0, -22.0); bx1, by1 = P(-116.9, -4.0)
ax.imshow(bar, extent=[bx0, bx0 + (bx1 - P(-119.0, -4.0)[0]) , by0, by1], zorder=8, aspect="auto")
ax.set_xlim(x0, x1); ax.set_ylim(y0, y1)
tx = bx0 + (bx1 - P(-119.0, -4.0)[0]) * 1.5
for latv, t in ((-4.6, "50% lost"), (-13.0, "0%"), (-21.4, "−50% (a net gain)")):
    ax.text(tx, P(-119.0, latv)[1], t, ha="left", va="center", fontsize=9.8, color=INK, zorder=8)
ax.text(bx0, P(-119.0, -1.6)[1], "Carbon gain lost\nto leakage", ha="left", va="bottom", fontsize=10.6, fontweight="bold", color=INK, zorder=8, linespacing=1.1)
ky = P(-119.0, -27.0)[1]
ax.plot([bx0, bx0 + 0.07], [ky, ky], color=NAV, linewidth=K * 2.0, solid_capstyle="round", zorder=8)
ax.text(bx0 + 0.09, ky, "Pulp trade; width shows tons", ha="left", va="center", fontsize=9.8, color=INK, zorder=8)
ky2 = P(-119.0, -30.5)[1]
ax.plot([bx0, bx0 + 0.07], [ky2, ky2], color=NAV, linewidth=1.5, linestyle=(0, (4, 2.5)), zorder=8)
ax.text(bx0 + 0.09, ky2, "One company's route", ha="left", va="center", fontsize=9.8, color=INK, zorder=8)

fig.text(0.03, 1 - 0.42 / H, "The wood behind a paper towel now travels farther", fontsize=23, fontweight="bold", color=INK, va="center")
fig.text(0.03, 1 - 0.98 / H, "When a mill closes, Americans keep buying paper and the fiber comes from farther away. Shading shows how much\nof the carbon gained by delaying harvests in a region is lost as cutting shifts somewhere else.",
         fontsize=11.6, color="#444444", va="center", linespacing=1.3)
fig.savefig(OUT, dpi=300, facecolor="white")
print("saved", OUT, round(W, 2), round(H, 2))
