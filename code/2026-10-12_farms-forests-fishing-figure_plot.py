"""Farms, forests and fishing: public figure for a general audience (NYT editorial register, minimal text).

Run: python3 2026-10-11_farms-forests-fishing-figure_plot.py <data_dir> <font_dir> <out_stem> <variant>
Variants: V1 four panels, resource plus first products boundary (farms include food processing)
          V2 three panels (value, carbon, research), same boundary
          V3 four panels, farms only boundary (BEA farms, NAICS 111-112)
Every number is read from <data_dir>. Python/matplotlib because R is not available in the sandbox.

Uncertainty: panel 1 whiskers are scenario ranges (carbon at $51 to $190 a ton; FAO and Cavender-Bares ranges),
not statistical intervals. Carbon panel dashed lines extend each sector's own 1990-2023 linear trend to 2050;
they are not forecasts. Fishing carbon is landings times a global fuel intensity (rough estimate).
"""
import os, sys, glob
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.gridspec import GridSpec
import numpy as np, pandas as pd

data, font_dir, out, variant = sys.argv[1:5]
for f in glob.glob(os.path.join(font_dir, "*.ttf")):
    fm.fontManager.addfont(f)
SANS, SERIF = "Libre Franklin", "Source Serif 4"
plt.rcParams.update({"font.family": SANS, "font.size": 13, "axes.unicode_minus": True,
                     "mathtext.fontset": "custom", "mathtext.rm": SANS, "mathtext.it": SANS})

INK, MUTED, FAINT, RULE = "#121212", "#4a4a4a", "#6b6b6b", "#e3e3e3"
FOREST, FARM, FISH = "#134a31", "#7d6b3a", "#1a6aa3"          # tan darkened for 4.5:1 text contrast
P = 0.12                                                       # $ thousand per t CO2e, i.e. $120 a ton -> $B per Mt
PLO, PHI = 0.051, 0.19
rd = lambda p: os.path.join(data, p)

# ---------------- data ----------------
g = pd.read_csv(rd("sector_green_nva_2022.csv")).set_index("sector")
sink = pd.read_csv(rd("epa_forest_sink_1990_2023.csv"))
farm_ghg = pd.read_csv(rd("epa_farm_emissions_1990_2022.csv"))
farm_ghg = farm_ghg[farm_ghg.scenario == "economic sector Agriculture"][["year", "value"]]   # includes on-farm fuel
land = pd.read_csv(rd("noaa_landings_1990_2023.csv"))
land = land[land.units == "million pounds"]
sc = pd.read_csv(rd("seafood_hidden_cost_estimate.csv")).set_index("item")
fund = pd.read_csv(rd("research_capacity_funds_fy2024.csv")).set_index("program")["usd_millions"]
nva = pd.read_csv(rd("bea_net_value_added_farms_forest_seafood.csv")) if os.path.exists(rd("bea_net_value_added_farms_forest_seafood.csv")) else None

F, A, M = g.loc["Forest"], g.loc["Agriculture"], g.loc["Marine"]
sink22 = float(sink.loc[sink.year == 2022, "net_uptake_mmt_co2e"].iloc[0])       # same EPA edition as the carbon panel
farm22 = float(farm_ghg.loc[farm_ghg.year == 2022, "value"].iloc[0])             # EPA economic sector, 2024 edition
intensity = sc.loc["fuel_intensity", "central"]
f_water, f_rec = 7.0, 14.0                    # national forest water (Sedell et al. 2000, inflated); recreation surplus (USFS 2018)

def full(nva_, carbon_mt, adj, price):        # net value added + carbon (+ uptake, - emissions) + other nature adjustment
    return nva_ + carbon_mt * price + adj

forest_other = (F.full_adj_mid + f_water + f_rec, F.full_adj_lo + f_water + f_rec, F.full_adj_hi + f_water + f_rec)
forest = dict(gdp=F.gva, mid=full(F.nva, sink22, forest_other[0], P),
              lo=full(F.nva, sink22, forest_other[1], PLO), hi=full(F.nva, sink22, forest_other[2], PHI))
if variant == "V3":
    fa = nva[(nva.sector == "Farms") & (nva.year == 2022)].iloc[0]
    a_gva, a_nva = fa.gva / 1e3, fa.nva / 1e3
else:
    a_gva, a_nva = A.gva, A.nva
farm = dict(gdp=a_gva, mid=full(a_nva, -farm22, A.full_adj_mid, P),
            lo=full(a_nva, -farm22, A.full_adj_lo, PHI), hi=full(a_nva, -farm22, A.full_adj_hi, PLO))
fleet = sc.loc["fleet_emissions", "central"]
fish = dict(gdp=M.gva, mid=full(M.nva, -fleet, 0, P), lo=full(M.nva, -fleet, 0, PHI), hi=full(M.nva, -fleet, 0, PLO))

t = pd.read_csv(rd("us_trade_ratio_1981_2025.csv")).drop_duplicates(["year", "sector"], keep="last")
t["bal"] = (t.X - t.M) / 1e9
tr = {s: t[t.sector == s].sort_values("year") for s in ("Agriculture", "Forest products", "Seafood")}
n_def, n_yr = int((tr["Forest products"].bal < 0).sum()), len(tr["Forest products"])

land_t = land.assign(mt=land.value * 0.45359237 / 1e3)        # million lb -> million t
fish_c = pd.DataFrame({"year": land_t.year, "value": -land_t.mt * intensity})
carbon = {"Forests": (sink[["year", "net_uptake_mmt_co2e"]].rename(columns={"net_uptake_mmt_co2e": "value"}), FOREST),
          "Farms": (farm_ghg.assign(value=-farm_ghg.value), FARM),
          "Fishing": (fish_c, FISH)}

# ---------------- figure scaffolding ----------------
def frame(ax, grid="y"):
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(INK); ax.spines["bottom"].set_linewidth(0.9)
    ax.tick_params(length=0, colors=MUTED, labelsize=12); ax.set_axisbelow(True)
    if grid: getattr(ax, f"{grid}axis").grid(True, color=RULE, lw=0.8)

def head(ax, title, sub):
    ax.text(0, 1.13, title, transform=ax.transAxes, fontsize=17, fontweight="bold", color=INK, va="bottom")
    ax.text(0, 1.04, sub, transform=ax.transAxes, fontsize=12, color=MUTED, va="bottom")

usd = lambda v: f"−${-v:,.0f}B" if v < 0 else f"${v:,.0f}B"

def panel_value(ax):
    head(ax, "Forests give about twice their GDP", "2022, billions of dollars")
    rows = [("Farms", farm, FARM), ("Forests", forest, FOREST), ("Fishing", fish, FISH)]
    lo_x = min(-100, min(r[1]["lo"] for r in rows) - 30)
    for i, (lab, d, c) in enumerate(rows):
        y = 2 - i
        ax.plot([d["lo"], d["hi"]], [y, y], color=c, lw=2, alpha=0.45, solid_capstyle="butt")
        for e in (d["lo"], d["hi"]): ax.plot([e, e], [y - 0.09, y + 0.09], color=c, lw=2, alpha=0.45)
        ax.annotate("", xy=(d["mid"], y), xytext=(d["gdp"], y),
                    arrowprops=dict(arrowstyle="-|>", color=c, lw=2.2, shrinkA=7, shrinkB=8, mutation_scale=16))
        ax.scatter([d["gdp"]], [y], s=90, facecolor="white", edgecolor=c, lw=2.2, zorder=4)
        ax.scatter([d["mid"]], [y], s=110, color=c, zorder=5)
        right = d["mid"] > d["gdp"]
        if lab == "Fishing":
            ax.text(max(d["gdp"], d["hi"]) + 30, y, f"{usd(d['gdp'])} to {usd(d['mid'])}".replace("$", r"\$"), color=c, fontsize=13, fontweight="bold", va="center")
        else:
            ax.text(d["mid"], y + 0.2, usd(d["mid"]), color=c, fontsize=14, fontweight="bold", ha="center", va="bottom")
            ax.text(d["gdp"], y + 0.2, usd(d["gdp"]), color=c, fontsize=12, ha="center", va="bottom")
    ax.scatter([280], [2.75], s=60, facecolor="white", edgecolor=MUTED, lw=1.8, clip_on=False)
    ax.text(300, 2.75, "GDP", fontsize=12, color=MUTED, va="center")
    ax.scatter([390], [2.75], s=70, color=MUTED, clip_on=False)
    ax.text(410, 2.75, "Counted in full", fontsize=12, color=MUTED, va="center")
    ax.set_yticks([2, 1, 0]); ax.set_yticklabels([r[0] for r in rows], fontsize=14, fontweight="bold", color=INK)
    ax.set_ylim(-0.5, 2.95); ax.set_xlim(lo_x, 620)
    ax.set_xticks([0, 200, 400, 600]); ax.set_xticklabels(["$0", "$200B", "$400B", "$600B"])
    ax.axvline(0, color=INK, lw=0.9); frame(ax, "x"); ax.spines["bottom"].set_visible(False)

def panel_trade(ax):
    head(ax, f"The U.S. buys more wood than it sells", "Exports minus imports, billions of dollars a year")
    ax.axhline(0, color=INK, lw=0.9)
    for s, c, lab, lw in (("Agriculture", FARM, "Farms", 2.6), ("Seafood", FISH, "Fishing", 2.6), ("Forest products", FOREST, "Forests", 3.6)):
        d = tr[s]; ax.plot(d.year, d.bal, color=c, lw=lw); ax.scatter([d.year.iloc[-1]], [d.bal.iloc[-1]], color=c, s=40, zorder=5)
    ends = {"Farms": tr["Agriculture"].bal.iloc[-1], "Fishing": tr["Seafood"].bal.iloc[-1], "Forests": tr["Forest products"].bal.iloc[-1]}
    ypos = {"Forests": ends["Forests"] + 4, "Fishing": ends["Fishing"] - 3, "Farms": ends["Farms"] - 2}
    for lab, c in (("Farms", FARM), ("Fishing", FISH), ("Forests", FOREST)):
        ax.text(2027, ypos[lab], lab, color=c, fontsize=13, fontweight="bold", va="center")
    ax.text(1982, 70, f"Wood: a deficit in {n_def} of {n_yr} years", fontsize=12.5, color=FOREST, fontweight="bold", va="center")
    ax.text(1982, 62, "Cutting less wood in one place shifts harvest elsewhere,\nthough the carbon effect can be much smaller (Daigneault et al. 2025)", fontsize=11, color=MUTED, va="top", linespacing=1.15)
    ax.set_xlim(1981, 2036); ax.set_ylim(-45, 75); ax.set_xticks([1985, 1995, 2005, 2015, 2025]); ax.spines["bottom"].set_bounds(1981, 2025.5)
    ax.set_yticks([-40, -20, 0, 20]); ax.set_yticklabels(["−$40B", "−$20B", "$0", "$20B"]); frame(ax)

def trend(d, to=2040):
    b = np.polyfit(d.year, d.value, 1); yrs = np.array([d.year.iloc[-1], to]); return yrs, np.polyval(b, yrs), b[0]

def panel_carbon(ax):
    head(ax, "Only forests store more than they release", "Million metric tons CO$_2$e a year, stored (+) or released (\u2212)")
    ax.axhline(0, color=INK, lw=0.9)
    labs = {}
    for lab, (d, c) in carbon.items():
        d = d.sort_values("year")
        yrs, yv, _ = trend(d)
        if lab != "Fishing": ax.plot(yrs, [d.value.iloc[-1], yv[1]], color=c, lw=2.4, ls=(0, (4, 3)), alpha=0.85)
        ax.plot(d.year, d.value, color=c, lw=2.0 if lab == "Fishing" else 3.4, zorder=3)
        if lab != "Fishing": ax.scatter(d.year, d.value, color=c, s=16, zorder=4)
        labs[lab] = (yv[1], c, d.value.iloc[-1], d.year.iloc[-1])
    off = {"Forests": 0, "Farms": 0, "Fishing": -150}
    for lab, (v, c, last, ly) in labs.items():
        ax.text(2042 if lab != "Fishing" else 2025, v + off[lab], (f"{lab}\n{last:,.0f}" + ("*" if lab == "Fishing" else f" ({ly})")).replace("-", "\u2212"),
                color=c, fontsize=13, fontweight="bold", va="center", linespacing=1.05)
    ax.text(2032, 1080, "dashed: 1990\u20132023 trend continued, not a forecast", fontsize=11, color=FAINT, ha="center", style="italic")
    ax.set_xlim(1988, 2058); ax.set_ylim(-850, 1200); ax.set_xticks([1990, 2015, 2040]); ax.spines["bottom"].set_bounds(1988, 2040.5)
    ax.set_yticks([-800, -400, 0, 400, 800]); ax.set_yticklabels(["−800", "−400", "0", "400", "800"]); frame(ax)

def panel_research(ax):
    head(ax, "Forests get a seventh of farm funds", "University research funds, 2024")
    bars = [("Farms", fund["Hatch"], FARM, "Hatch"), ("Fishing*", fund["Sea Grant core plus aquaculture"], FISH, "Sea Grant"), ("Forests", fund["McIntire-Stennis"], FOREST, "McIntire-Stennis")]
    for i, (lab, v, c, prog) in enumerate(bars):
        ax.barh(2 - i, v, color=c, height=0.6)
        ax.text(v + 6, 2 - i + 0.08, f"${v:.0f}M", va="center", fontsize=15, fontweight="bold", color=c)
        ax.text(v + 6, 2 - i - 0.22, prog, va="center", fontsize=11, color=MUTED)
    ax.set_yticks([2, 1, 0]); ax.set_yticklabels([b[0] for b in bars], fontsize=14, fontweight="bold", color=INK)
    ax.set_xlim(0, 330); ax.set_xticks([]); ax.set_ylim(-0.6, 2.6)
    for s in ("top", "right", "bottom"): ax.spines[s].set_visible(False)
    ax.spines["left"].set_color(INK); ax.tick_params(length=0)

# ---------------- layout ----------------
four = variant in ("V1", "V3")
if four:
    fig = plt.figure(figsize=(32 / 2.54, 23 / 2.54), dpi=300)
    gs = GridSpec(2, 2, hspace=0.55, wspace=0.28, left=0.075, right=0.955, top=0.835, bottom=0.115)
    axes = [fig.add_subplot(gs[i, j]) for i in (0, 1) for j in (0, 1)]
    panels = [panel_value, panel_trade, panel_carbon, panel_research]
    ytitle = 0.955
else:
    fig = plt.figure(figsize=(40 / 2.54, 14.5 / 2.54), dpi=300)
    gs = GridSpec(1, 3, wspace=0.36, left=0.055, right=0.975, top=0.73, bottom=0.2)
    axes = [fig.add_subplot(gs[0, j]) for j in range(3)]
    panels = [panel_value, panel_carbon, panel_research]
    ytitle = 0.95
fig.patch.set_facecolor("white")
for ax, p in zip(axes, panels): p(ax)
fig.text(0.035, ytitle, "Of farms, forests and fishing, only forests give back more than GDP counts", fontsize=22 if four else 25, fontweight="bold", family=SERIF, color=INK, va="top")

boundary = ("Farms are farm production only; forests include wood and paper mills; fishing includes seafood processing" if variant == "V3"
            else "Each sector includes its processing (food, wood and paper, seafood)")
fig.text(0.035, 0.018,
         f"{boundary}. Counted in full: GDP less wear and tear, plus carbon at $120 a ton (bars: $51 to $190) and nature's other costs and benefits.\n"
         "Clean air value covers all U.S. trees. Carbon from EPA; dots mark reported years. *Fishing is estimated from landings; Sea Grant also funds coastal work." + (" Trade: UN Comtrade, nominal dollars." if four else "") + "\n"
         "Data and methods: doi.org/10.5281/zenodo.23122535. Weiskittel, Daigneault and Woodall, University of Maine.",
         fontsize=9.5 if four else 10, color=FAINT, va="bottom", linespacing=1.4)

fig.savefig(out + ".png", dpi=300, facecolor="white"); fig.savefig(out + ".pdf", facecolor="white")
tf = {k: trend(v[0].sort_values("year")) for k, v in carbon.items()}
print(variant, {k: {kk: round(vv, 1) for kk, vv in d.items()} for k, d in (("farm", farm), ("forest", forest), ("fish", fish))},
      "ratio", round(forest["mid"] / forest["gdp"], 2), round(forest["lo"] / forest["gdp"], 2), round(forest["hi"] / forest["gdp"], 2),
      "deficit", n_def, n_yr, "trend2050", {k: round(v[1][1]) for k, v in tf.items()}, "slopes", {k: round(v[2], 2) for k, v in tf.items()})
