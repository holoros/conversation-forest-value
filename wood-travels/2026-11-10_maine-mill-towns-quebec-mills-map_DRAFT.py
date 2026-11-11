# Maine mill towns, operating pulp mills and Quebec border mills, for the Conversation sequel.
# Python rebuild of the R map (the R host was offline on November 10, 2026); carries every element forward
# and adds Maine's operating pulp mills and a full legend.
# Inputs, all in this folder unless noted:
#   2026-06-25_quebec-mills-within-50km-of-maine_DATA.csv  Gouvernement du Quebec list of permitted mills (CC BY 4.0)
#   2020_cec-land-cover-forest-layer_DATA.png              forest classes, CEC 2020 North American land cover, 30 m
#   us-atlas states-10m.json and world-atlas countries-10m.json (npm packages, Natural Earth and Census outlines)
# Usage: python3 this_script.py <atlas_dir> <out_png>
import csv, json, sys, math
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.lines import Line2D
from matplotlib.patches import PathPatch, FancyBboxPatch
from matplotlib.path import Path
import matplotlib.patheffects as pe
from PIL import Image
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ATLAS, OUT = sys.argv[1], sys.argv[2]
for f in ("LiberationSans-Regular", "LiberationSans-Bold", "LiberationSans-Italic", "LiberationSerif-Bold"):
    fm.fontManager.addfont(f"/usr/share/fonts/truetype/liberation/{f}.ttf")
plt.rcParams["font.family"] = "Liberation Sans"
GRN, RED, NAV, LBLU, ORG = "#1F4D36", "#A23B2A", "#2F6C9E", "#8DB7D8", "#D9692E"
LAND, SEA, INK, GRY = "#E8E6E1", "#F4F8FB", "#2B2B2B", "#6E6E6E"
X0, X1, Y0, Y1 = -73.6, -65.4, 42.95, 47.95


def topo_rings(path, obj, keep=None):
    """Return a list of (id, [ring arrays]) from a TopoJSON file, decoded to lon/lat."""
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
    res = []
    for g in t["objects"][obj]["geometries"]:
        gid = g.get("id") or g.get("properties", {}).get("name")
        if keep and gid not in keep:
            continue
        polys = g["arcs"] if g["type"] == "MultiPolygon" else [g["arcs"]]
        res.append((gid, [ring(r) for p in polys for r in p]))
    return res


def patch(rings, **kw):
    verts, codes = [], []
    for r in rings:
        if r[:, 0].max() < X0 - 3 or r[:, 0].min() > X1 + 3 or r[:, 1].max() < Y0 - 3 or r[:, 1].min() > Y1 + 3:
            continue
        verts += list(r)
        codes += [Path.MOVETO] + [Path.LINETO] * (len(r) - 2) + [Path.CLOSEPOLY]
    return PathPatch(Path(verts, codes), **kw) if verts else None


states = topo_rings(f"{ATLAS}/us-atlas/states-10m.json", "states")
canada = topo_rings(f"{ATLAS}/world-atlas/countries-10m.json", "countries", keep={"124"})
maine = [s for s in states if s[0] == "23"]

fig = plt.figure(figsize=(10, 7.9), dpi=300)
ax = fig.add_axes([0.126, 0.03, 0.748, 0.825])
ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1)
ax.set_aspect(1 / math.cos(math.radians((Y0 + Y1) / 2)))
ax.set_facecolor(SEA); ax.set_xticks([]); ax.set_yticks([])
for s in ax.spines.values():
    s.set_visible(False)
for gid, rings in canada + states:
    pt = patch(rings, facecolor=LAND, edgecolor="none", zorder=1)
    if pt is not None:
        ax.add_patch(pt)
forest = np.asarray(Image.open(os.path.join(HERE, "2020_cec-land-cover-forest-layer_DATA.png")).convert("RGBA")) / 255.0
ax.imshow(forest, extent=(X0, X1, Y0, Y1), zorder=2, interpolation="bilinear", aspect="auto")
for gid, rings in canada + states:
    pt = patch(rings, facecolor="none", edgecolor="white", linewidth=0.7, zorder=3)
    if pt is not None:
        ax.add_patch(pt)
ax.add_patch(patch(maine[0][1], facecolor="none", edgecolor=GRN, linewidth=1.5, zorder=4))

# Quebec mills within 50 km of Maine
q = list(csv.DictReader(open(os.path.join(HERE, "2026-06-25_quebec-mills-within-50km-of-maine_DATA.csv"), encoding="utf-8")))
saw = [r for r in q if r["catcomplet"].startswith("2")]
oth = [r for r in q if not r["catcomplet"].startswith("2")]
def dot_size(r):
    """Dot area scales with the upper bound of the mill's permitted annual wood volume class."""
    upper = float(r["clascomplet"].split(" - ")[-1].replace(" ", "").replace("\u202f", "").replace("\xa0", ""))
    return 28 + 240 * math.sqrt(upper / 1.3e6)


for rows, col in ((oth, LBLU), (saw, NAV)):
    rows = sorted(rows, key=dot_size, reverse=True)
    ax.scatter([float(r["longitude"]) for r in rows], [float(r["latitude"]) for r in rows], s=[dot_size(r) for r in rows], c=col,
               edgecolors="white", linewidths=0.6, zorder=6, alpha=0.92)

closed = [  # town label, lon, lat, label lon, label lat
    ("Millinocket\nclosed 2008", -68.710, 45.657, -70.21, 46.11),
    ("East Millinocket\nclosed 2014", -68.574, 45.627, -68.38, 46.37),
    ("Bucksport\nclosed 2014", -68.795, 44.574, -68.47, 43.93),
    ("Lincoln\nclosed 2015", -68.505, 45.362, -66.42, 45.80),
    ("Old Town\nclosed 2015, reopened,\nclosed again 2023", -68.645, 44.934, -66.72, 44.42),
    ("Madison\nclosed 2016; TimberHP now\nmakes insulation there", -69.880, 44.798, -72.47, 44.83),
    ("Jay\nclosed 2023", -70.216, 44.504, -72.05, 43.78),
    ("Nackawic, N.B.\npulp mill idled 2026", -67.240, 45.997, -66.33, 46.45),
]
newuse = [
    ("Ashland\nWholeTrees makes beams\nfrom whole tree trunks", -68.406, 46.631, -66.93, 47.02),
    ("Saco\nTanbark makes food\ncontainers from wood fiber", -70.443, 43.501, -71.85, 43.27),
]
pulp = [  # operating pulp mills: name, note, lon, lat, text dx, dy, ha
    ("Rumford", "$330M+ invested since 2019", -70.551, 44.553, -0.11, 0.0, "right"),
    ("Skowhegan", "$600M invested since 2018", -69.640, 44.700, 0.11, 0.10, "left"),
    ("Baileyville", "paused wood buying in 2025", -67.403, 45.156, 0.11, 0.0, "left"),
    ("Saint John, N.B.", "$1.1B upgrade announced 2024", -66.060, 45.270, -0.33, 0.15, "center"),
]
paper = [  # paper mill still operating without a pulp mill
    ("Westbrook", "paper machine shut in 2020", -70.371, 43.677, 0.11, 0.03, "left"),
]
box = dict(boxstyle="round,pad=0.32,rounding_size=0.18", fc="white", ec=INK, lw=0.7)


def label(txt, x, y, lx, ly):
    ax.annotate(txt, xy=(x, y), xytext=(lx, ly), ha="center", va="center", fontsize=8.6, color=INK, linespacing=1.12,
                bbox=box, zorder=9, arrowprops=dict(arrowstyle="-", color=GRY, lw=0.9, shrinkA=0, shrinkB=5))


for t, x, y, lx, ly in closed:
    label(t, x, y, lx, ly)
for t, x, y, lx, ly in newuse:
    label(t, x, y, lx, ly)
ax.scatter([c[1] for c in closed], [c[2] for c in closed], marker="x", s=150, c=RED, linewidths=3.0, zorder=8)
ax.scatter([c[1] for c in newuse], [c[2] for c in newuse], marker="^", s=170, c=GRN, edgecolors="white", linewidths=0.6, zorder=8)
ax.scatter([p[2] for p in pulp], [p[3] for p in pulp], marker="s", s=120, c=ORG, edgecolors="white", linewidths=0.9, zorder=8)
ax.scatter([p[2] for p in paper], [p[3] for p in paper], marker="s", s=105, c="white", edgecolors=ORG, linewidths=2.2, zorder=8)
halo = [pe.withStroke(linewidth=2.6, foreground="white")]
for n, note, x, y, dx, dy, ha in pulp + paper:
    ax.text(x + dx, y + dy + 0.045, n, ha=ha, va="center", fontsize=8.4, color=INK, fontweight="bold", path_effects=halo, zorder=9)
    ax.text(x + dx, y + dy - 0.045, note, ha=ha, va="center", fontsize=7.8, color=INK, path_effects=halo, zorder=9)

ax.text(-73.3, 47.25, f"Quebec: {len(q)} wood mills operate within\n30 miles of Maine, {len(saw)} of them sawmills", ha="left", va="center",
        fontsize=9.8, color=NAV, fontweight="bold", linespacing=1.15, zorder=9,
        bbox=dict(boxstyle="round,pad=0.35,rounding_size=0.18", fc="white", ec="none"))

ax.text(-73.3, 47.03, "Dot size follows each mill's permitted wood volume", ha="left", va="center", fontsize=7.8, color=NAV,
        path_effects=halo, zorder=9)

ax.text(-66.35, 47.55, "Other New Brunswick\nmills are not mapped", ha="center", va="center", fontsize=7.8, color=GRY, fontstyle="italic",
        linespacing=1.1, path_effects=halo, zorder=9)

# ownership box
ax.add_patch(FancyBboxPatch((-70.10, 42.99), 2.16, 0.53, boxstyle="round,pad=0,rounding_size=0.05", fc="white", ec=INK, lw=0.7, zorder=10))
ax.text(-70.00, 43.435, "Who owns the forest", ha="left", va="center", fontsize=9.8, color=GRN, fontweight="bold", zorder=11)
ax.text(-70.00, 43.355, "Maine: 92% private\nQuebec: 92% public overall\nNew Brunswick: 51% public", ha="left", va="top",
        fontsize=9.0, color=INK, linespacing=1.25, zorder=11)

handles = [
    Line2D([], [], marker="x", color="none", markeredgecolor=RED, markersize=9, markeredgewidth=2.6, label="Pulp or paper mill closed or idled"),
    Line2D([], [], marker="s", color="none", markerfacecolor=ORG, markeredgecolor="white", markersize=9, label="Pulp mill still operating"),
    Line2D([], [], marker="s", color="none", markerfacecolor="white", markeredgecolor=ORG, markeredgewidth=1.8, markersize=8, label="Paper mill still operating"),
    Line2D([], [], marker="o", color="none", markerfacecolor=NAV, markeredgecolor="white", markersize=8, label="Quebec sawmill"),
    Line2D([], [], marker="o", color="none", markerfacecolor=LBLU, markeredgecolor="white", markersize=8, label="Other Quebec wood mill"),
    Line2D([], [], marker="^", color="none", markerfacecolor=GRN, markeredgecolor="white", markersize=9, label="New use for wood"),
    Line2D([], [], marker="s", color="none", markerfacecolor="#96C4A0", markeredgecolor="none", markersize=10, label="Forest"),
]
leg = ax.legend(handles=handles, loc="lower right", bbox_to_anchor=(0.995, 0.012), fontsize=8.4, frameon=True, framealpha=1,
                edgecolor=INK, fancybox=True, borderpad=0.7, labelspacing=0.55, handletextpad=0.5)
leg.get_frame().set_linewidth(0.7); leg.set_zorder(12)

fig.text(0.126, 0.955, "When a pulp mill closes, sawmills feel it too", fontfamily="Liberation Serif", fontweight="bold", fontsize=21,
         color=GRN, ha="left", va="center")
fig.text(0.126, 0.899, "Sawmills sell their chips and sawdust to pulp mills, so each closure reaches well beyond the mill town.\n"
         "Maine has lost seven paper mills since 2008, and the survivors have needed costly upgrades.",
         fontsize=10.6, color=INK, ha="left", va="center", linespacing=1.3)
fig.savefig(OUT, dpi=300, facecolor="white")
print(len(q), len(saw), "saved", OUT)
