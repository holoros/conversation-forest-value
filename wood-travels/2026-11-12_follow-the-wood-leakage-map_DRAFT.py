# Follow the wood with a leakage layer, rebuilt November 12, 2026, in Python.
# Shading: colors read from figure 2a of Daigneault et al. 2025 (Environ. Res. Lett. 20:114022, CC BY 4.0;
# `2025_daigneault-erl-fig2a-leakage-layer_DATA.png`) and assigned to each Global Timber Model region and forest
# type code on Adam Daigneault's 0.5 degree forest type grid (not in this repository; pass its CSV with X, Y, code).
# Each code takes the most common figure color among its cells, so the shading is the published figure redrawn
# on the model's own grid. No leakage value is computed here.
# Routes are schematic. Usage: python3 <script> <node_modules dir> <grid.csv> <out.png>
import csv, json, sys, os, math, collections
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import PathPatch, FancyArrowPatch
from matplotlib.path import Path
import matplotlib.patheffects as pe
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ATLAS, GRID, OUT = sys.argv[1], sys.argv[2], sys.argv[3]
plt.rcParams["font.family"] = "Liberation Sans"
GRN, NAV, LAND, SEA, INK, GRY = "#1F4D36", "#12355B", "#E8E6E1", "#F4F8FB", "#2B2B2B", "#6E6E6E"
X0, X1, Y0, Y1 = -100.0, -30.0, -38.0, 54.0


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


def add_poly(ax, rings, **kw):
    verts, codes = [], []
    for r in rings:
        if r[:, 0].max() < X0 - 5 or r[:, 0].min() > X1 + 5 or r[:, 1].max() < Y0 - 5 or r[:, 1].min() > Y1 + 5 or r[:, 0].max() - r[:, 0].min() > 300:
            continue
        verts += list(map(tuple, r))
        codes += [Path.MOVETO] + [Path.LINETO] * (len(r) - 2) + [Path.CLOSEPOLY]
    if verts:
        ax.add_patch(PathPatch(Path(verts, codes), **kw))


# ---- leakage colors by forest type code ----
lay = np.array(Image.open(os.path.join(HERE, "2025_daigneault-erl-fig2a-leakage-layer_DATA.png")).convert("RGB")).astype(int)
SC, LX0 = 3.745, -177.5
LYMX = 314.7 / SC
rows = [(float(r["X"]), float(r["Y"]), int(r["code"])) for r in csv.DictReader(open(GRID))]
votes = collections.defaultdict(collections.Counter)
hit = 0
for x, y, c in rows:
    px, py = int(round((x - LX0) * SC)), int(round((LYMX - y) * SC))
    if 0 <= px < lay.shape[1] and 0 <= py < lay.shape[0]:
        r, g, b = lay[py, px]
        if max(r, g, b) - min(r, g, b) > 95 and r > 190:      # a leakage color, not gray land, white sea or text
            votes[c][(r // 8 * 8, g // 8 * 8, b // 8 * 8)] += 1
            hit += 1
colr = {c: np.array(v.most_common(1)[0][0]) / 255.0 for c, v in votes.items() if sum(v.values()) >= 3}
print("cells", len(rows), "with a figure color", hit, "codes colored", len(colr))

dx = 0.499306
nx, ny = int(round((X1 - X0) / dx)) + 2, int(round((Y1 - Y0) / dx)) + 2
img = np.zeros((ny, nx, 4))
for x, y, c in rows:
    if c in colr and X0 - dx <= x <= X1 + dx and Y0 - dx <= y <= Y1 + dx:
        i, j = int(round((x - X0) / dx)), int(round((Y1 - y) / dx))
        if 0 <= i < nx and 0 <= j < ny:
            img[j, i, :3] = colr[c]; img[j, i, 3] = 1

fig = plt.figure(figsize=(10, 10.2), dpi=300)
ax = fig.add_axes([0.03, 0.02, 0.94, 0.855])
ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1); ax.set_aspect(1.0); ax.set_axis_off()
ax.add_patch(plt.Rectangle((X0, Y0), X1 - X0, Y1 - Y0, facecolor=SEA, edgecolor="none", zorder=0))
world = topo(f"{ATLAS}/world-atlas/countries-50m.json", "countries")
states = topo(f"{ATLAS}/us-atlas/states-10m.json", "states")
for name, rings in world.items():
    add_poly(ax, rings, facecolor=LAND, edgecolor="none", zorder=1)
ax.imshow(img, extent=[X0 - dx / 2, X0 - dx / 2 + nx * dx, Y1 + dx / 2 - ny * dx, Y1 + dx / 2], interpolation="nearest", zorder=2)
# clip the raster to land so cells do not spill into the sea
verts, codes = [], []
for rings in world.values():
    for r in rings:
        if r[:, 0].max() < X0 - 5 or r[:, 0].min() > X1 + 5 or r[:, 1].max() < Y0 - 5 or r[:, 1].min() > Y1 + 5 or r[:, 0].max() - r[:, 0].min() > 300:
            continue
        verts += list(map(tuple, r)); codes += [Path.MOVETO] + [Path.LINETO] * (len(r) - 2) + [Path.CLOSEPOLY]
ax.images[0].set_clip_path(PathPatch(Path(verts, codes), transform=ax.transData))
for name, rings in world.items():
    add_poly(ax, rings, facecolor="none", edgecolor="white", linewidth=0.5, zorder=3)
for name, rings in states.items():
    add_poly(ax, rings, facecolor="none", edgecolor="white", linewidth=0.35, zorder=3)
add_poly(ax, states["Maine"], facecolor="none", edgecolor="#0B2A1B", linewidth=1.8, zorder=5)

# ---- routes over the ocean (schematic) ----
def route(p0, c1, c2, p1):
    path = Path([p0, c1, c2, p1], [Path.MOVETO, Path.CURVE4, Path.CURVE4, Path.CURVE4])
    ax.add_patch(FancyArrowPatch(path=path, arrowstyle="-|>,head_length=9,head_width=5", color=NAV, linewidth=2.6, zorder=6))
SJ, MAC, BR, EAST = (-66.06, 45.27), (-83.63, 32.84), (-51.7, -20.8), (-76.3, 36.9)
route(SJ, (-60.0, 39.0), (-70.0, 27.5), (MAC[0] + 0.9, MAC[1] - 0.25))   # Saint John, down the Atlantic, in through the Georgia coast
route(BR, (-31.0, -24.0), (-47.0, 24.0), EAST)                    # Brazil, out to the Atlantic, up to U.S. ports
for p in (SJ, MAC, BR):
    ax.scatter(*p, s=70, c=INK, edgecolors="white", linewidths=0.8, zorder=7)

box = dict(boxstyle="round,pad=0.35", facecolor="white", edgecolor=INK, linewidth=0.6)
def lab(x, y, t, ha="center", va="center"):
    ax.text(x, y, t, ha=ha, va=va, fontsize=10.6, color=INK, bbox=box, zorder=8, linespacing=1.2)
lab(-63.5, 49.6, "Saint John, N.B.\npulp mill", ha="left")
lab(-91.5, 28.3, "Macon, Ga.\nSaint John pulp\nbecomes tissue")
ax.plot([-55.5, -68.4], [36.6, 44.7], color=GRY, linewidth=0.7, zorder=6)
lab(-47.5, 32.0, "Maine logs cross the border to Quebec\nsawmills. In 2023, about 2 million tons of\nMaine's harvest left the state unprocessed,\nwhile 2.7 million tons came in from\nneighboring states and provinces")
lab(-47.0, -31.5, "Brazil supplies about 82% of\nthe hardwood pulp the U.S. imports,\nmostly from eucalyptus plantations")
ax.text(-69.2, 48.6, "MAINE", ha="center", va="center", fontsize=11, fontweight="bold", color=GRN, zorder=8,
        path_effects=[pe.withStroke(linewidth=3, foreground="white")])

# ---- legend ----
bar = np.array(Image.open(os.path.join(HERE, "2025_daigneault-erl-fig2-legend-bar_DATA.png")).convert("RGB"))
ax.imshow(bar, extent=[-96.5, -94.6, -24.0, -6.0], zorder=8, aspect="auto")
ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1)
for yv, t in ((-6.6, "50% lost"), (-15.0, "0%"), (-23.4, "−50% (a net gain)")):
    ax.text(-93.9, yv, t, ha="left", va="center", fontsize=9.8, color=INK, zorder=8)
ax.text(-96.5, -3.6, "Carbon gain lost\nto leakage", ha="left", va="bottom", fontsize=10.4, fontweight="bold", color=INK, zorder=8, linespacing=1.1)

fig.text(0.03, 0.955, "The wood behind a paper towel now travels farther", fontsize=24, fontweight="bold", color=GRN, family="Liberation Serif", va="center")
fig.text(0.03, 0.905, "When a mill closes, Americans keep buying paper and the fiber comes from farther away. Shading shows how much\nof the carbon gained by delaying harvests in a region is lost as cutting shifts somewhere else.",
         fontsize=11.6, color=INK, va="center", linespacing=1.3)
fig.savefig(OUT, dpi=300, facecolor="white")
print("saved", OUT)
