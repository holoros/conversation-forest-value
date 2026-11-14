# U.S. net trade in logs, wood products, pulp, and paper by world region, 2024: map plus bought and sold bars.
# Built November 14, 2026. Input (same folder): 2024_us-wood-trade-by-world-region-faf5_DATA.csv
# (Freight Analysis Framework 5.6.1 data tabulation tool, SCTG 25 to 28, current $M, 2024 estimates).
# The New Zealand note is UN Comtrade, U.S.-reported imports of HS 44 from partner 554 in 2024 ($251.2M).
# Usage: python3 <script> <node_modules dir with world-atlas> <out.png>
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



world = topo(f"{ATLAS}/world-atlas/countries-110m.json", "countries")
reg = {r["region"]: (float(r["import_musd"]), float(r["export_musd"])) for r in csv.DictReader(open(os.path.join(HERE, "2024_us-wood-trade-by-world-region-faf5_DATA.csv")))}
imp = sum(v[0] for v in reg.values()); exp_ = sum(v[1] for v in reg.values()); nneg = sum(1 for v in reg.values() if v[1] < v[0])
_kt = list(csv.DictReader(open(os.path.join(HERE, "2024_us-wood-trade-by-world-region-faf5_DATA.csv")))); kti = sum(float(r["import_kt"]) for r in _kt); kto = sum(float(r["export_kt"]) for r in _kt)
print("kt in", kti, "kt out", kto, "usd per ton in", imp / kti * 1000, "out", exp_ / kto * 1000)
print("imports", imp, "exports", exp_, "net", exp_ - imp, "regions selling the U.S. more:", nneg)
B = lambda v: f"\\${v / 1000 + 1e-9:.1f}B"
K = 26 / math.sqrt(11244)
pos = {"Canada": (-104.0, 57.0), "Mexico": (-102.0, 23.5), "Rest of Americas": (-58.0, -12.0), "Europe": (14.0, 50.0), "Africa": (20.0, 3.0),
       "SW & Central Asia": (62.0, 30.0), "Eastern Asia": (112.0, 35.0), "SE Asia & Oceania": (130.0, -14.0)}
nice = {"Rest of Americas": "Rest of the Americas", "SW & Central Asia": "Southwest and\nCentral Asia", "SE Asia & Oceania": "Southeast Asia\nand Oceania"}
BUY, SELL = "#2B5C8A", "#D9692E"

fig = plt.figure(figsize=(10, 5.9), dpi=300); fig.patch.set_facecolor("white")
fig.text(0.04, 0.94, f"The U.S. spends more on wood and paper than it earns in {['zero','one','two','three','four','five','six','seven','eight'][nneg]} of eight world regions", fontweight="bold", fontsize=16.4, color="#1A1A1A", ha="left", va="center")
fig.text(0.04, 0.878, f"In 2024 the U.S. bought {B(imp)} of logs, wood products, pulp, and paper abroad and sold {B(exp_)}, federal estimates show. It shipped out more\ntons than it brought in, but a ton coming in was worth about \\${imp / kti * 1000:,.0f} and a ton going out about \\${exp_ / kto * 1000:,.0f}, a sign that raw\nmaterials leave and value-added products come back. Circle area is the dollar gap, U.S. sold minus bought.", fontsize=10.6, color=INK, ha="left", va="center", linespacing=1.3)

ax = fig.add_axes([0.02, 0.07, 0.66, 0.74]); ax.set_axis_off(); ax.set_aspect("equal")
for name, rings in world.items():
    if name == "Antarctica":
        continue
    add_poly(ax, rings, equal_earth, facecolor="#BDBAB2" if name == "United States of America" else LAND, edgecolor="white", linewidth=0.35, zorder=1)
x0, _ = equal_earth(np.array([-170.0]), np.array([0.0])); x1, _ = equal_earth(np.array([180.0]), np.array([0.0]))
_, y0 = equal_earth(np.array([0.0]), np.array([-56.0])); _, y1 = equal_earth(np.array([0.0]), np.array([84.0]))
ax.set_xlim(x0[0], x1[0]); ax.set_ylim(y0[0], y1[0])
lab = {"Canada": (0, 0, "center"), "Mexico": (22, -8, "left"), "Rest of Americas": (20, 0, "left"), "Europe": (0, 24, "center"), "Africa": (10, -2, "left"),
       "SW & Central Asia": (0, -24, "center"), "Eastern Asia": (0, 20, "center"), "SE Asia & Oceania": (0, -30, "center")}
for k, (i, o) in sorted(reg.items(), key=lambda t: -abs(t[1][1] - t[1][0])):
    net = o - i; x, y = equal_earth(np.array([pos[k][0]]), np.array([pos[k][1]])); col = SELL if net > 0 else BUY
    ax.scatter(x, y, s=(2 * K * math.sqrt(abs(net))) ** 2, c=col, edgecolors=col, linewidths=0.8, alpha=0.60, zorder=3, clip_on=False)
    dx, dy, ha = lab[k]; amt = (B(abs(net)) if abs(net) >= 1000 else f"\\${abs(net):.0f}M")
    txt = f"{nice.get(k, k)}\n{'+' if net > 0 else '−'}{amt}"
    ax.annotate(txt, (x[0], y[0]), xytext=(dx, dy), textcoords="offset points", ha=ha, va="center", fontsize=9.4, fontweight="bold", color="white" if k == "Canada" else INK,
                path_effects=None if k == "Canada" else halo, zorder=5, linespacing=1.1)
pp = (imp - exp_) * 1e6 / 341785457                      # U.S. resident population, Census Bureau July 1, 2025 estimates (sum of the state file)
xu, yu = equal_earth(np.array([-117.0]), np.array([33.0])); xt, yt = equal_earth(np.array([-166.0]), np.array([-4.0]))
ax.annotate(f"UNITED STATES\nbought {B(imp)}\nsold {B(exp_)}\ngap {B(imp - exp_)}\n\\${pp:.0f} per resident", (xu[0], yu[0]), xytext=(xt[0], yt[0]), textcoords="data", ha="left", va="top",
            fontsize=9.4, fontweight="bold", color=INK, path_effects=halo, arrowprops=dict(arrowstyle="-", color=INK, lw=0.8, relpos=(0.3, 1.0)), zorder=6, linespacing=1.2)
xn, yn = equal_earth(np.array([172.0]), np.array([-42.0]))
ax.annotate("New Zealand: \\$251M of wood products\nsold to the U.S. (U.N. data)", (xn[0], yn[0]), xytext=(-12, -22), textcoords="offset points", ha="right", va="center", fontsize=9, color=INK,
            path_effects=halo, arrowprops=dict(arrowstyle="-", color=INK, lw=0.7), zorder=6, linespacing=1.15)
for i, (c, t) in enumerate([(BUY, "U.S. buys more than it sells"), (SELL, "U.S. sells more than it buys")]):
    fig.text(0.055, 0.165 - 0.04 * i, "●", color=c, fontsize=13, ha="center", va="center"); fig.text(0.07, 0.165 - 0.04 * i, t, fontsize=9.4, color=INK, ha="left", va="center")

b = fig.add_axes([0.80, 0.16, 0.19, 0.60]); order = sorted(reg, key=lambda k: reg[k][0] - reg[k][1], reverse=True)
for j, k in enumerate(order):
    y = len(order) - 1 - j; i, o = reg[k]
    b.barh(y + 0.19, i, height=0.36, color=BUY); b.barh(y - 0.19, o, height=0.36, color=SELL)
    b.text(-600, y, nice.get(k, k).replace("\n", " ").replace("Southwest and Central Asia", "SW and Central Asia").replace("Southeast Asia and Oceania", "SE Asia and Oceania"), ha="right", va="center", fontsize=9.2, fontweight="bold", color=INK)
    b.text(max(i, o) + 500, y, f"{B(i)} / {B(o)}", ha="left", va="center", fontsize=9, color=INK)
b.set_xlim(0, 37000); b.set_ylim(-0.7, len(order) - 0.3); b.set_axis_off()
fig.text(0.80, 0.80, "U.S. BOUGHT", fontsize=10, fontweight="bold", color=BUY, ha="left", va="center"); fig.text(0.905, 0.80, "/ SOLD", fontsize=10, fontweight="bold", color=SELL, ha="left", va="center")
fig.text(0.04, 0.035, "Modeled estimates from the federal Freight Analysis Framework (2024). Wooden furniture, not counted here, adds a gap of about \\$14B (U.N. data).\nCenter for Research on Sustainable Forests, University of Maine.", fontsize=9, color=GRY, ha="left", va="center", linespacing=1.3)
fig.savefig(OUT, dpi=300, facecolor="white"); print("saved", OUT)
