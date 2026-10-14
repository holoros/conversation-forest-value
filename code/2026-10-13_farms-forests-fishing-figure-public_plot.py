"""Farms, forests and fishing: four-panel public figure built to carry the Conversation case (October 13, 2026).

Run: python3 2026-10-13_farms-forests-fishing-figure-public_plot.py <data_dir> <font_dir> <icon_dir> none <out_stem> <variant>
Variants: case   value (with net wood imports beneath it), carbon, wood trade, funding (2 x 2)
          hero   value and funding only, 16:9 for social and slides
Public release. The article's story and stack variants add a forest crowding panel built from an
unpublished analysis; that panel, its inputs and its gates are withheld until peer review.
Same data and gates as 2026-10-13_farms-forests-fishing-figure_plot.py. Changes for a general audience:
panel A shows value per $1 of GDP (one scale for all three sectors), panels follow the argument
(value, carbon, markets, funding), forests lead every panel, sector icons key the colors,
and the carbon panel drops its 2040 trend extension in favor of the observed 17% decline.
Icons: Material Design Icons (Pictogrammers), Apache License 2.0.
Uncertainty: panel A whiskers are scenario ranges (carbon at $51 to $190 a ton and the FAO and
Cavender-Bares ranges), not statistical intervals. The other panels are reported values.
"""
import os, sys, glob, io
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker
from matplotlib import font_manager as fm
from matplotlib.gridspec import GridSpec
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import PathPatch
from matplotlib.transforms import Affine2D
import numpy as np, pandas as pd, warnings, re
GLYPH_MISS = []
_sw = warnings.showwarning
warnings.showwarning = lambda m, *a, **k: (GLYPH_MISS.append(str(m)) if 'missing from font' in str(m) else _sw(m, *a, **k))
from svgpath2mpl import parse_path

data, font_dir, icon_dir, crowd_csv, out, variant = sys.argv[1:7]
import textwrap
EXC_DIR = sys.argv[7] if len(sys.argv) > 7 else os.path.dirname(crowd_csv)
for f in glob.glob(os.path.join(font_dir, "*.ttf")):
    fm.fontManager.addfont(f)
SANS, SERIF = "Libre Franklin", "Source Serif 4"
plt.rcParams.update({"font.family": SANS, "font.size": 13, "axes.unicode_minus": True,
                     "mathtext.fontset": "custom", "mathtext.rm": SANS, "mathtext.it": SANS})
INK, MUTED, FAINT, RULE, GREY = "#121212", "#4a4a4a", "#6b6b6b", "#e3e3e3", "#a8a8a8"
FOREST, FARM, FISH = "#134a31", "#7d6b3a", "#1a6aa3"
P, PLO, PHI = 0.12, 0.051, 0.19
rd = lambda p: os.path.join(data, p)

# ---------------- data (identical to the selected four-panel script) ----------------
g = pd.read_csv(rd("sector_green_nva_2022.csv")).set_index("sector")
sink = pd.read_csv(rd("epa_forest_sink_1990_2023.csv"))
farm_ghg = pd.read_csv(rd("epa_farm_emissions_1990_2022.csv"))
farm_ghg = farm_ghg[farm_ghg.scenario == "economic sector Agriculture"][["year", "value"]]
land = pd.read_csv(rd("noaa_landings_1990_2023.csv")); land = land[land.units == "million pounds"]
sc = pd.read_csv(rd("seafood_hidden_cost_estimate.csv")).set_index("item")
fund = pd.read_csv(rd("research_capacity_funds_fy2024.csv")).set_index("program")["usd_millions"]
F, A, M = g.loc["Forest"], g.loc["Agriculture"], g.loc["Marine"]
sink22 = float(sink.loc[sink.year == 2022, "net_uptake_mmt_co2e"].iloc[0])
farm22 = float(farm_ghg.loc[farm_ghg.year == 2022, "value"].iloc[0])
intensity = sc.loc["fuel_intensity", "central"]
f_water, f_rec = 7.0, 14.0
full = lambda n, c, adj, p: n + c * p + adj
fo = (F.full_adj_mid + f_water + f_rec, F.full_adj_lo + f_water + f_rec, F.full_adj_hi + f_water + f_rec)
forest = dict(gdp=F.gva, mid=full(F.nva, sink22, fo[0], P), lo=full(F.nva, sink22, fo[1], PLO), hi=full(F.nva, sink22, fo[2], PHI))
farm = dict(gdp=A.gva, mid=full(A.nva, -farm22, A.full_adj_mid, P), lo=full(A.nva, -farm22, A.full_adj_lo, PHI), hi=full(A.nva, -farm22, A.full_adj_hi, PLO))
fleet = sc.loc["fleet_emissions", "central"]
fish = dict(gdp=M.gva, mid=full(M.nva, -fleet, 0, P), lo=full(M.nva, -fleet, 0, PHI), hi=full(M.nva, -fleet, 0, PLO))
t = pd.read_csv(rd("us_trade_ratio_1981_2025.csv")).drop_duplicates(["year", "sector"], keep="last")
t["bal"] = (t.X - t.M) / 1e9
tr = {s: t[t.sector == s].sort_values("year") for s in ("Agriculture", "Forest products", "Seafood")}
n_def, n_yr = int((tr["Forest products"].bal < 0).sum()), len(tr["Forest products"])
land_t = land.assign(mt=land.value * 0.45359237 / 1e3)
fish_c = pd.DataFrame({"year": land_t.year, "value": -land_t.mt * intensity}).sort_values("year")
sink_s = sink.sort_values("year"); farm_s = farm_ghg.sort_values("year")
s90, s23 = float(sink_s.iloc[0].net_uptake_mmt_co2e), float(sink_s.iloc[-1].net_uptake_mmt_co2e)
drop = 100 * (1 - s23 / s90)

HAS_CROWD = crowd_csv.lower() != "none"   # public release: crowding analysis withheld until peer review
if variant not in ("case", "hero"): sys.exit("story and stack variants need the unpublished crowding inputs; use case or hero")
if HAS_CROWD:
    pass  # crowding inputs are not used by the public variants
noair = (forest["mid"] - float(F.full_adj_mid)) / forest["gdp"]   # forest value without the clean air credit

# ---------------- helpers ----------------
def icon_img(name, color, px=160):
    d = re.search(r'd="([^"]+)"', open(os.path.join(icon_dir, name + ".svg")).read()).group(1)
    path = parse_path(d).transformed(Affine2D().scale(1, -1).translate(0, 24))
    f = plt.figure(figsize=(1, 1), dpi=px); a = f.add_axes([0, 0, 1, 1]); a.set_xlim(0, 24); a.set_ylim(0, 24); a.axis("off")
    a.add_patch(PathPatch(path, facecolor=color, edgecolor="none"))
    buf = io.BytesIO(); f.savefig(buf, format="png", transparent=True, dpi=px); plt.close(f); buf.seek(0)
    return plt.imread(buf)
ICON = {"Forests": ("forest", FOREST), "Farms": ("barley", FARM), "Fishing": ("fish", FISH)}
IMG = {k: icon_img(*v) for k, v in ICON.items()}

def put_icon(ax, lab, xy, zoom=0.17, coords="axes fraction"):
    ax.add_artist(AnnotationBbox(OffsetImage(IMG[lab], zoom=zoom), xy, xycoords=coords, frameon=False, box_alignment=(0.5, 0.5), annotation_clip=False))

def frame(ax, grid="y"):
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(INK); ax.spines["bottom"].set_linewidth(0.9)
    ax.tick_params(length=0, colors=MUTED, labelsize=12); ax.set_axisbelow(True)
    if grid: getattr(ax, f"{grid}axis").grid(True, color=RULE, lw=0.8)

HEADS = []
AX2 = []
def head(ax, title, sub):
    if variant == "stack": sub, title = textwrap.fill(sub, 46), textwrap.fill(title, 32)
    big = variant != "stack"
    from matplotlib.transforms import blended_transform_factory as btf
    xy, xc = ((0.06, 1.0), (btf(ax.figure.transFigure, ax.transAxes))) if variant == "stack" else ((0, 1.0), ax.transAxes)
    st = ax.annotate(sub, xy, xycoords=xc, xytext=(0, 9), textcoords="offset points", fontsize=12 if big else 11, color=MUTED, va="bottom", linespacing=1.15, annotation_clip=False)
    tt = ax.annotate(title, xy, xycoords=xc, xytext=(0, 30), textcoords="offset points", fontsize=(16 if variant == "story" else 17) if big else 14.5, fontweight="bold", color=INK, va="bottom", linespacing=1.1, annotation_clip=False)
    HEADS.append((st, tt))

def finalize_heads(fig):
    fig.canvas.draw(); R = fig.canvas.get_renderer(); k = fig.dpi / 72
    for st, tt in HEADS:
        tt.xyann = (0, 9 + st.get_window_extent(R).height / k + 4)

def ylabels(ax, labs, ys):
    ax.set_yticks([]); fs = 14 if variant != "stack" else 12.5
    for lab, y in zip(labs, ys):
        c = ICON[lab][1]
        ax.add_artist(AnnotationBbox(OffsetImage(IMG[lab], zoom=0.17 if variant != "stack" else 0.14), (0, y), xycoords=("axes fraction", "data"),
                                     xybox=(-22, 0), boxcoords="offset points", frameon=False, annotation_clip=False))
        ax.annotate(lab, (0, y), xycoords=("axes fraction", "data"), xytext=(-40, 0), textcoords="offset points",
                    ha="right", va="center", fontsize=fs, fontweight="bold", color=c, annotation_clip=False)

# ---------------- panels ----------------
ROWS = [("Forests", forest), ("Farms", farm), ("Fishing", fish)]

def panel_value(ax):
    head(ax, "Forests are worth nearly twice their GDP", "Counting nature's costs and benefits, per \\$1 of GDP, 2022")
    ys = [2, 1, 0]
    for (lab, d), y in zip(ROWS, ys):
        c = ICON[lab][1]; r, lo, hi = d["mid"] / d["gdp"], d["lo"] / d["gdp"], d["hi"] / d["gdp"]
        ax.barh(y, r, height=0.52, color=c, alpha=1 if lab == "Forests" else 0.75, zorder=3)
        ax.plot([lo, hi], [y, y], color=INK, lw=1.4, zorder=4)
        for e in (lo, hi): ax.plot([e, e], [y - 0.1, y + 0.1], color=INK, lw=1.4, zorder=4)
        ax.text(max(hi, r, 1.0) + 0.08, y, f"\\${r:.2f}", va="center", fontsize=(22 if lab == "Forests" else 16) - (4 if variant == "stack" else 0), fontweight="bold", color=c)
    ax.scatter([noair], [2], marker="D", s=46, facecolor="white", edgecolor=INK, lw=1.3, zorder=6)
    ax.text(noair - 0.07, 2, f"\\${noair:.2f}", ha="right", va="center", fontsize=10.5 if variant != "stack" else 9, color="white", fontweight="bold", zorder=7)
    ax.axvline(1, color=INK, lw=1.2, ls=(0, (3, 2)), zorder=5)
    ax.text(1.04, 2.62, r"\$1 of GDP", fontsize=12, fontweight="bold", color=INK, va="center")
    ylabels(ax, [r[0] for r in ROWS], ys)
    ax.set_xlim(-0.15, 3.25); ax.set_ylim(-0.55, 2.8)
    ax.set_xticks([0, 1, 2, 3]); ax.set_xticklabels(["$0", "$1", "$2", "$3"]); frame(ax, "x")
    ax.set_xlabel(r"Value per \$1 of GDP", fontsize=12 if variant != "stack" else 10.5, fontweight="bold", color=INK, labelpad=4)
    if INSET_IMPORTS and variant in ("story", "stack"):
        w = tr["Forest products"]; ni = -w.bal; n_imp = int((ni > 0).sum())
        ia = ax.inset_axes([0.6, 0.17, 0.39, 0.3] if variant != "stack" else [0.6, 0.18, 0.39, 0.28])
        ia.set_facecolor("white"); ia.patch.set_alpha(1); ia.set_zorder(7)
        ia.bar(w.year, ni, width=0.85, color=[FOREST if v > 0 else "#b9c4bd" for v in ni])
        ia.axhline(0, color=INK, lw=0.7)
        for s_ in ("top", "right", "left"): ia.spines[s_].set_visible(False)
        ia.spines["bottom"].set_visible(False)
        ia.set_xlim(1980, 2026.5); ia.set_ylim(-3, 26)
        ia.set_xticks([1985, 2025]); ia.set_yticks([0, 20]); ia.set_yticklabels(["\\$0", "\\$20B"])
        ia.tick_params(length=0, labelsize=9.5 if variant != "stack" else 9, colors=MUTED, pad=1)
        ia.set_title((f"Net wood imports, imports exceed\nexports in {n_imp} of {len(ni)} years" if variant != "stack" else f"Net wood imports,\n{n_imp} of {len(ni)} years"), fontsize=10 if variant != "stack" else 9, fontweight="bold", color=FOREST, loc="left", pad=3, linespacing=1.05)
        NETIMP.extend([n_imp, len(ni), float(ni.sum())])

def panel_carbon(ax):
    head(ax, "Only forests store more than they release", "Million metric tons CO$_2$e a year, stored (+) or released (−)")
    ax.axhline(0, color=INK, lw=0.9, zorder=2)
    ax.fill_between(sink_s.year, 0, sink_s.net_uptake_mmt_co2e, color=FOREST, alpha=0.16, lw=0)
    ax.plot(sink_s.year, sink_s.net_uptake_mmt_co2e, color=FOREST, lw=3.2, marker="o", ms=4.5, zorder=3)
    ax.fill_between(farm_s.year, 0, -farm_s.value, color=FARM, alpha=0.16, lw=0)
    ax.plot(farm_s.year, -farm_s.value, color=FARM, lw=3.2, marker="o", ms=4.5, zorder=3)
    ax.plot(fish_c.year, fish_c.value, color=FISH, lw=2.2, zorder=3)
    ax.annotate(f"Down {drop:.0f}% since 1990", xy=(2023, s23), xytext=(1990, 1250), fontsize=13 if variant != "stack" else 11.5, fontweight="bold", color=FOREST,
                arrowprops=dict(arrowstyle="-|>", color=FOREST, lw=1.4, connectionstyle="arc3,rad=-0.2"))
    fs = 13 if variant != "stack" else 11.5
    ax.text(2006, 700, f"Forests store {s23:,.0f} (2023)", color=FOREST, fontsize=fs, fontweight="bold", ha="center", va="top")
    ax.text(2006, 70, f"Fishing releases {-fish_c.value.iloc[-1]:.0f}*", color=FISH, fontsize=fs, fontweight="bold", ha="center", va="bottom")
    ax.text(2006, -470, f"Farms release {farm_s.value.iloc[-1]:,.0f} (2022)", color=FARM, fontsize=fs, fontweight="bold", ha="center", va="bottom")
    ax.set_xlim(1988, 2025); ax.set_ylim(-850, 1320); ax.set_xticks([1990, 2000, 2010, 2020]); ax.spines["bottom"].set_bounds(1988, 2023.5)
    yt = [-800, -400, 0, 400, 800] if variant != "stack" else [-400, 0, 400, 800]
    ax.set_yticks(yt); ax.set_yticklabels([f"{v:,}".replace("-", "\u2212") for v in yt]); frame(ax)
    ax.set_xlabel("Year", fontsize=12 if variant != "stack" else 10.5, fontweight="bold", color=INK, labelpad=4)
    ax.set_ylabel("Mt CO$_2$e a year", fontsize=12 if variant != "stack" else 10.5, fontweight="bold", color=INK, labelpad=6)

SHARE = "#5b6770"
RISK = "#a8452f"
INSET_IMPORTS = False
STRIP = []
NETIMP = []
CROWD_BINS = []
def panel_netimp(ax):
    head(ax, "The U.S. buys more wood than it sells", "Net imports of wood and paper products, billions of dollars")
    w = tr["Forest products"]; ni = -w.bal
    ax.bar(w.year, ni, width=0.8, color=[FOREST if v > 0 else "#b9c4bd" for v in ni], zorder=2)
    ax.axhline(0, color=INK, lw=0.9, zorder=3)
    n_imp, tot = int((ni > 0).sum()), float(ni.sum())
    ax.text(1982, 37.5 if variant != "stack" else 45.5, f"Net importer in {n_imp} of {len(ni)} years", fontsize=12.5 if variant != "stack" else 11, fontweight="bold", color=FOREST, va="top")
    ax.annotate("while U.S. pulp capacity fell about\na quarter since 2015" if variant != "stack" else "while U.S. pulp capacity fell\nabout a quarter since 2015", (1982, 37.5 if variant != "stack" else 45.5),
                xytext=(0, -20 if variant != "stack" else -17), textcoords="offset points", fontsize=11 if variant != "stack" else 10, color=MUTED, va="top", linespacing=1.1)
    ax.set_xlim(1980, 2026.5); ax.set_ylim(-4, 38 if variant != "stack" else 46); ax.set_xticks([1985, 2000, 2015] if variant == "stack" else [1985, 1995, 2005, 2015, 2025])
    ax.set_yticks([0, 10, 20]); ax.set_yticklabels(["$0", "$10B", "$20B"]); frame(ax)
    ax.set_xlabel("Year", fontsize=12 if variant != "stack" else 10.5, fontweight="bold", color=INK, labelpad=4)
    ax.set_ylabel("Net imports", fontsize=12 if variant != "stack" else 10.5, fontweight="bold", color=INK, labelpad=6)
    NETIMP.extend([n_imp, len(ni), tot])

def panel_import_strip(ax):
    w = tr["Forest products"]; ni = -w.bal; n_imp = int((ni > 0).sum())
    ax.bar(w.year, ni, width=0.8, color=[FOREST if v > 0 else "#b9c4bd" for v in ni], zorder=2)
    ax.axhline(0, color=INK, lw=0.9, zorder=3)
    ax.set_xlim(1980, 2026.5); ax.set_ylim(-3, 27)
    ax.set_xticks([1985, 1995, 2005, 2015, 2025] if variant != "stack" else [1985, 2005, 2025])
    ax.set_yticks([0, 20]); ax.set_yticklabels(["\\$0", "\\$20B"]); frame(ax)
    ax.tick_params(labelsize=11 if variant != "stack" else 10)
    ax.text(0, 1.06, f"The U.S. also buys more wood than it sells ({n_imp} of {len(ni)} years)" if variant != "stack" else f"Net wood imports in {n_imp} of {len(ni)} years",
            transform=ax.transAxes, fontsize=12.5 if variant != "stack" else 11, fontweight="bold", color=FOREST, va="bottom")
    ax.set_ylabel("Net imports", fontsize=11 if variant != "stack" else 10, fontweight="bold", color=INK, labelpad=4)
    ax.set_xlabel("Year", fontsize=11 if variant != "stack" else 10, fontweight="bold", color=INK, labelpad=3)
    NETIMP.extend([n_imp, len(ni), float(ni.sum())])

def panel_trade(ax):
    head(ax, "The U.S. buys more wood than it sells", "Exports minus imports, billions of dollars a year")
    ax.axhline(0, color=INK, lw=0.9)
    w = tr["Forest products"]
    for s, lab in (("Agriculture", "Farms"), ("Seafood", "Fishing")):
        d = tr[s]; ax.plot(d.year, d.bal, color=GREY, lw=1.8, zorder=2)
    ax.fill_between(w.year, 0, w.bal.clip(upper=0), color=FOREST, alpha=0.18, lw=0)
    ax.plot(w.year, w.bal, color=FOREST, lw=3.6, zorder=4); ax.scatter([w.year.iloc[-1]], [w.bal.iloc[-1]], color=FOREST, s=45, zorder=5)
    ends = {"Forests": (w.bal.iloc[-1] + 5, FOREST), "Fishing": (tr["Seafood"].bal.iloc[-1] - 4, GREY), "Farms": (tr["Agriculture"].bal.iloc[-1] - 1, GREY)}
    for lab, (y, c) in ends.items():
        ax.text(2027, y, lab, color=c if lab == "Forests" else MUTED, fontsize=13, fontweight="bold", va="center")
    ax.text(1982, 72, f"Wood: a deficit in {n_def} of {n_yr} years", fontsize=13, color=FOREST, fontweight="bold", va="center")
    ax.text(1982, 64, "U.S. pulp capacity has fallen about a quarter since 2015,\nleaving fewer domestic buyers for small trees", fontsize=11.5, color=MUTED, va="top", linespacing=1.15)
    ax.set_xlim(1981, 2036); ax.set_ylim(-45, 78); ax.set_xticks([1985, 1995, 2005, 2015, 2025]); ax.spines["bottom"].set_bounds(1981, 2025.5)
    ax.set_yticks([-40, -20, 0, 20]); ax.set_yticklabels(["−$40B", "−$20B", "$0", "$20B"]); frame(ax)
    ax.set_xlabel("Year", fontsize=12 if variant != "stack" else 10.5, fontweight="bold", color=INK, labelpad=4)
    ax.set_ylabel("Exports minus imports", fontsize=12 if variant != "stack" else 10.5, fontweight="bold", color=INK, labelpad=6)

def panel_research(ax):
    head(ax, "Yet forests get a seventh of farm funds", "Federal formula funds for university research, 2024")
    bars = [("Forests", fund["McIntire-Stennis"], "McIntire-Stennis"), ("Farms", fund["Hatch"], "Hatch"), ("Fishing", fund["Sea Grant core plus aquaculture"], "Sea Grant*")]
    ys = [2, 1, 0]
    for (lab, v, prog), y in zip(bars, ys):
        c = ICON[lab][1]
        ax.barh(y, v, color=c, height=0.52, alpha=1 if lab == "Forests" else 0.75)
        ax.text(v + 6, y + (0.1 if variant != "stack" else 0.14), f"${v:.0f}M", va="center", fontsize=(22 if lab == "Forests" else 16) - (4 if variant == "stack" else 0), fontweight="bold", color=c)
        ax.text(v + 6, y - (0.33 if variant != "stack" else 0.48), prog, va="center", fontsize=11 if variant != "stack" else 10, color=MUTED)
    ylabels(ax, [b[0] for b in bars], ys)
    ax.set_xlim(0, 330); ax.set_xticks([]); ax.set_ylim(-0.55, 2.8)
    ax.set_xlabel("Research funds, millions of dollars a year", fontsize=12 if variant != "stack" else 10.5, fontweight="bold", color=INK, labelpad=8)
    for s in ("top", "right", "bottom", "left"): ax.spines[s].set_visible(False)
    ax.axvline(0, color=INK, lw=0.9)

# ---------------- layout ----------------
HEAD = {"case": "Forests are worth more than markets count, yet get a seventh of farms' research funds",
        "hero": "Forests are worth the most per dollar of GDP and get the least research money"}[variant]
DECK = {"hero": "U.S. farms, forests and fishing, each counted with its processing industries"}.get(variant,
        "U.S. farms, forests and fishing compared, each counted with its processing industries")
PANELS = {"case": (panel_value, panel_carbon, panel_trade, panel_research),
          "hero": (panel_value, panel_research)}[variant]
uses = {p.__name__ for p in PANELS}
notes = [r"Value per \$1 of GDP: GDP less wear and tear, plus carbon at \$120 a ton and nature's other costs and benefits, divided by GDP. Black bars: carbon at \$51 to \$190 a ton. Diamond: forests without the clean air credit." if "panel_value" in uses else None,
         "Each sector includes its processing (food, wood and paper, seafood). Clean air value covers all U.S. trees. *Fishing is estimated from landings, and Sea Grant also funds coastal work.",
         ("Carbon from EPA, dots mark reported years. " if "panel_carbon" in uses else "") + ("Trade: UN Comtrade, nominal dollars." if ("panel_trade" in uses or "panel_netimp" in uses or variant in ("story", "stack")) else ""),
         "Data and methods: doi.org/10.5281/zenodo.23122535. Weiskittel, Daigneault and Woodall, University of Maine."]
notes = [n for n in notes if n and n.strip()]
if variant == "case":
    fig = plt.figure(figsize=(34 / 2.54, 26 / 2.54), dpi=300)
    gs = GridSpec(2, 2, hspace=0.66, wspace=0.62, left=0.13, right=0.96, top=0.77, bottom=0.215)
    axes = [fig.add_subplot(gs[i, j]) for i in (0, 1) for j in (0, 1)]
    hsz, wrap, foot_sz, ty, dy = 20, 200, 9.5, 0.965, 0.915
elif variant == "story":
    from matplotlib.gridspec import GridSpecFromSubplotSpec
    fig = plt.figure(figsize=(36 / 2.54, 31 / 2.54), dpi=300)
    gs = GridSpec(2, 2, hspace=0.6, wspace=0.62, left=0.12, right=0.955, top=0.79, bottom=0.2, height_ratios=[1.2, 1])
    sub = GridSpecFromSubplotSpec(2, 1, subplot_spec=gs[0, 1], height_ratios=[2.7, 1], hspace=0.95)
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(sub[0]), fig.add_subplot(gs[1, 0]), fig.add_subplot(gs[1, 1])]
    STRIP.append(fig.add_subplot(sub[1]))
    hsz, wrap, foot_sz, ty, dy = 21, 200, 9.5, 0.965, 0.915
elif variant == "stack":
    fig = plt.figure(figsize=(14 / 2.54, 52 / 2.54), dpi=300)
    from matplotlib.gridspec import GridSpecFromSubplotSpec
    gs = GridSpec(4, 1, hspace=0.95, left=0.34, right=0.84, top=0.83, bottom=0.215, height_ratios=[1.45, 1.75, 1, 1])
    sub = GridSpecFromSubplotSpec(2, 1, subplot_spec=gs[1, 0], height_ratios=[2.2, 1], hspace=1.2)
    axes = [fig.add_subplot(gs[0, 0]), fig.add_subplot(sub[0]), fig.add_subplot(gs[2, 0]), fig.add_subplot(gs[3, 0])]
    STRIP.append(fig.add_subplot(sub[1]))
    hsz, wrap, foot_sz, ty, dy = 17, 34, 9, 0.985, 0.93
    notes = [textwrap.fill(n, 62) for n in notes]
else:
    fig = plt.figure(figsize=(33.87 / 2.54, 19.05 / 2.54), dpi=300)
    gs = GridSpec(1, 2, wspace=0.45, left=0.14, right=0.955, top=0.70, bottom=0.25)
    axes = [fig.add_subplot(gs[0, j]) for j in range(2)]
    hsz, wrap, foot_sz, ty, dy = 23, 200, 10.5, 0.95, 0.86
    notes = [textwrap.fill(n, 175) for n in notes]
fig.patch.set_facecolor("white")
for ax, p in zip(axes, PANELS): p(ax)
for ax in STRIP: panel_import_strip(ax)
axes = axes + STRIP
X0 = 0.035 if variant != "stack" else 0.06
ht = fig.text(X0, ty, textwrap.fill(HEAD, wrap if variant != "stack" else 30), fontsize=hsz, fontweight="bold", family=SERIF, color=INK, va="top", linespacing=1.15)
fig.canvas.draw(); hb = ht.get_window_extent(fig.canvas.get_renderer())
fig.text(X0, hb.y0 / fig.bbox.height - 10 / 72 / fig.get_size_inches()[1], textwrap.fill(DECK, 52 if variant == "stack" else 200), fontsize=13 if variant != "stack" else 11, color=MUTED, va="top")
finalize_heads(fig)
fig.text(0.035 if variant != "stack" else 0.06, 0.012, "\n".join(notes), fontsize=foot_sz, color=FAINT, va="bottom", linespacing=1.4)

# ---------------- gates (hard exits, external anchors) ----------------
ratio = forest["mid"] / forest["gdp"]
gates = {"wood deficit 43 of 45 years (UN Comtrade)": (n_def, n_yr) == (43, 45),
         "forest GDP 120 to 150 $B (BEA 2022)": 120 < forest["gdp"] < 150,
         "forest ratio 1.5 to 2.7 (Zenodo scenario range)": 1.5 < ratio < 2.7,
         "only forests above $1 at every carbon price": forest["lo"] > forest["gdp"] and farm["hi"] < farm["gdp"] and fish["hi"] < fish["gdp"],
         "Hatch / McIntire-Stennis 6.5 to 7.5 (APLU FY2024)": 6.5 < fund["Hatch"] / fund["McIntire-Stennis"] < 7.5,
         "sink decline 16 to 18% (EPA GHGI 1990 to 2023)": 16 < drop < 18,
         "clean air sensitivity 1.7 to 1.8 (sector analysis, $42B Cavender-Bares credit)": 1.7 < noair < 1.8,
         "net importer 43 of 45 years (UN Comtrade)": NETIMP[:2] == [43, 45] if NETIMP else variant not in ("story", "stack"),
         "forests lowest research funds on every basis (raw, per GDP, per full value)": all(
             fund["McIntire-Stennis"] / den_f < min(fund["Hatch"] / den_a, fund["Sea Grant core plus aquaculture"] / den_m)
             for den_f, den_a, den_m in ((1, 1, 1), (forest["gdp"], farm["gdp"], fish["gdp"]), (forest["mid"], farm["mid"], fish["mid"])))}
fig.canvas.draw(); R = fig.canvas.get_renderer(); W, H = fig.bbox.width, fig.bbox.height
clip = [t.get_text()[:30] for t in fig.findobj(matplotlib.text.Text) if t.get_text().strip() and t.get_visible()
        and (lambda b: b.x0 < -1 or b.y0 < -1 or b.x1 > W + 1 or b.y1 > H + 1)(t.get_window_extent(R))]
gates["no text clipped at canvas edge"] = not clip
arts = [t for t in fig.findobj(matplotlib.text.Text) if t.get_text().strip() and t.get_visible()]
bbs = [(t.get_text()[:25].replace("\n", " "), matplotlib.text.Text.get_window_extent(t, R)) for t in arts]   # text box only, not an annotation's leader line
hits = [(a, b) for i, (a, A) in enumerate(bbs) for (b, B) in bbs[i + 1:]
        if min(A.x1, B.x1) - max(A.x0, B.x0) > 2 and min(A.y1, B.y1) - max(A.y0, B.y0) > 2]
if hits: print("overlaps:", hits[:12])
gates["no overlapping text"] = not hits
gates["no glyphs missing from the fonts"] = not GLYPH_MISS
imgs = [a.get_window_extent(R) for a in fig.findobj(AnnotationBbox)]
gates["icons inside canvas"] = all(b.x0 >= 0 and b.x1 <= W and b.y0 >= 0 and b.y1 <= H for b in imgs)
mathy = [t.get_text()[:40] for t in fig.findobj(matplotlib.text.Text)
         if len(re.findall(r"(?<!\\)\$", t.get_text().replace("CO$_2$", ""))) >= 2]
if mathy: print("unescaped $ pairs:", mathy)
gates["no stray mathtext from unescaped dollar signs"] = not mathy
foot = fig.texts[-1].get_window_extent(R).y1
for ax in axes: ax.xaxis.label.set_visible(True)
ticks = min([l.get_window_extent(R).y0 for ax in axes for l in ax.get_xticklabels() if l.get_text()] + [ax.xaxis.label.get_window_extent(R).y0 for ax in axes if ax.get_xlabel()] + [ax.get_window_extent(R).y0 for ax in axes])
gates["footnote clears tick labels"] = foot < ticks - 4
bad = [k for k, v in gates.items() if not v]
if clip: print("clipped:", clip)
if bad: sys.exit("GATE FAIL: " + "; ".join(bad))
fig.savefig(out + ".png", dpi=300, facecolor="white"); fig.savefig(out + ".pdf", facecolor="white")
print({lab: (round(d["mid"] / d["gdp"], 2), round(d["lo"] / d["gdp"], 2), round(d["hi"] / d["gdp"], 2)) for lab, d in ROWS}, "drop", round(drop, 1))
