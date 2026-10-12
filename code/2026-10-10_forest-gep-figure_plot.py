"""Four panel public figure: undervalued, misunderstood, at risk, underinvested.
NYT editorial register for a broad, non-technical audience: one claim per panel, direct labels, minimal text.
Python/matplotlib (R is not available in the sandbox). Every number is read from the data folder.

Run: python3 code/2026-10-10_forest-gep-figure_plot.py data <font_dir> figures/2026-10-10_forest-gep-figure_DRAFT
Inputs in <data>: sector_green_nva_2022.csv, us_trade_ratio_1981_2025.csv, epa_forest_sink_1990_2023.csv,
research_capacity_funds_fy2024.csv. Fonts: Libre Franklin and Source Serif 4 TTFs (SIL OFL); missing fonts fall
back to the default sans.

Uncertainty: panel 1 shows scenario ranges (carbon at $51 to $190 per t; FAO hidden cost range) as faint bars.
Trade values and appropriations are official statistics with no published sampling error; EPA's annual sink
uncertainty is not drawn; panel 3 paths after 2023 are illustrations, not forecasts. Stated in the source line.
"""
import os, sys, glob
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.gridspec import GridSpec
import numpy as np, pandas as pd

data, font_dir, out = sys.argv[1:4]
for f in glob.glob(os.path.join(font_dir, "*.ttf")):
    fm.fontManager.addfont(f)
SANS, SERIF = "Libre Franklin", "Source Serif 4"
plt.rcParams.update({"font.family": SANS, "font.size": 13, "text.parse_math": False, "axes.unicode_minus": True,
                     "mathtext.fontset": "custom", "mathtext.rm": SANS})

INK, MUTED, FAINT, RULE = "#121212", "#4a4a4a", "#767676", "#e3e3e3"
FOREST, FARM, SEA, RISK = "#134a31", "#9a8a5f", "#1a75b4", "#c9333b"
usd = lambda x: f"${x:,.0f}B"

# ---------------- data ----------------
g = pd.read_csv(os.path.join(data, "sector_green_nva_2022.csv")).set_index("sector")
F, A, M = g.loc["Forest"], g.loc["Agriculture"], g.loc["Marine"]
f_water, f_rec = 7.0, 14.0                       # national forest water (Sedell et al. 2000, inflated), recreation (USFS 2018)
forest = [F.gva, F.nva, F.green_mid, F.full_mid + f_water + f_rec]
forest_lo = [None, None, F.green_lo, F.nva + (F.green_lo - F.nva) + F.full_adj_lo + f_water + f_rec]
forest_hi = [None, None, F.green_hi, F.nva + (F.green_hi - F.nva) + F.full_adj_hi + f_water + f_rec]
farm = [A.gva, A.nva, A.green_mid, A.full_mid]
farm_lo = [None, None, A.green_hi, A.full_lo]     # green_hi/lo are reversed for a net emitter
farm_hi = [None, None, A.green_lo, A.full_hi]

t = pd.read_csv(os.path.join(data, "us_trade_ratio_1981_2025.csv")).drop_duplicates(["year", "sector"], keep="last")
t["net"] = (t.M - t.X) / 1e9
fp = t[t.sector == "Forest products"].sort_values("year"); sf = t[t.sector == "Seafood"].sort_values("year"); ag = t[t.sector == "Agriculture"].sort_values("year")
farm_ghg = -(A.nva - A.green_mid) / 0.12   # direct farm emissions, million t CO2e (EPA 2022), recovered from the $120/t charge
n_def, n_yr = int((fp.net > 0).sum()), len(fp)

sink = pd.read_csv(os.path.join(data, "epa_forest_sink_1990_2023.csv"))
fund = pd.read_csv(os.path.join(data, "research_capacity_funds_fy2024.csv")).set_index("program")["usd_millions"]
sc = pd.read_csv(os.path.join(data, "seafood_hidden_cost_estimate.csv")).set_index("item")   # rough estimates, see basis column

# ---------------- layout ----------------
fig = plt.figure(figsize=(32 / 2.54, 25 / 2.54), dpi=300)
fig.patch.set_facecolor("white")
gs = GridSpec(2, 2, hspace=0.62, wspace=0.26, left=0.06, right=0.96, top=0.765, bottom=0.14)
fig.text(0.04, 0.965, "U.S. forests give back about twice what the economy records,", fontsize=26, fontweight="bold",
         family=SERIF, color=INK, va="top")
fig.text(0.04, 0.925, "and wood not grown here is cut somewhere else", fontsize=26, fontweight="bold",
         family=SERIF, color=INK, va="top")

def frame(ax):
    for s in ("top", "right", "left"): ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color(INK); ax.spines["bottom"].set_linewidth(0.9)
    ax.tick_params(length=0, colors=MUTED, labelsize=12); ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=RULE, lw=0.8)

def head(ax, eyebrow, color, title, sub):
    ax.text(0, 1.30, eyebrow, transform=ax.transAxes, fontsize=12, fontweight="bold", color=color, va="bottom")
    ax.text(0, 1.15, title, transform=ax.transAxes, fontsize=17, fontweight="bold", color=INK, va="bottom")
    ax.text(0, 1.05, sub, transform=ax.transAxes, fontsize=12, color=MUTED, va="bottom", parse_math=True)

# ---------------- 1. undervalued ----------------
ax = fig.add_subplot(gs[0, 0])
head(ax, "UNDERVALUED", FOREST, "Count what forests give, and they rival farms", "Yearly value in 2022, adding what markets do not price")
x = np.arange(4)
for vals, lo, hi, col in ((farm, farm_lo, farm_hi, FARM), (forest, forest_lo, forest_hi, FOREST)):
    for i in (2, 3):
        ax.plot([x[i], x[i]], [lo[i], hi[i]], color=col, lw=8, alpha=0.3, solid_capstyle="butt")
    ax.plot(x, vals, color=col, lw=4, solid_capstyle="round", zorder=3)
    ax.scatter(x, vals, color=col, s=70, zorder=4)
fc, lr = sc.loc["fleet_carbon_cost"], sc.loc["lost_rent"]
sea = [M.gva, M.nva, M.nva - fc.central, M.nva - fc.central - lr.central]
ax.plot(x, sea, color=SEA, lw=3, zorder=3); ax.scatter(x, sea, color=SEA, s=50, zorder=4)
ax.text(3.15, sea[3] - 12, f"Seafood {usd(sea[3])}*", color=SEA, fontsize=13, fontweight="bold", va="center")
ax.text(-0.12, farm[0], usd(farm[0]), color=FARM, fontsize=13, fontweight="bold", ha="right", va="center")
ax.text(-0.12, forest[0] + 10, usd(forest[0]), color=FOREST, fontsize=13, fontweight="bold", ha="right", va="center")
ax.text(-0.12, sea[0] - 5, usd(sea[0]), color=SEA, fontsize=13, fontweight="bold", ha="right", va="center")
ax.text(3.15, farm[3] - 45, f"Farms\n{usd(farm[3])}", color=FARM, fontsize=14, fontweight="bold", va="center", linespacing=1.1)
ax.text(3.15, forest[3] + 45, f"Forests\n{usd(forest[3])}", color=FOREST, fontsize=14, fontweight="bold", va="center", linespacing=1.1)
ax.set_xticks(x); ax.set_xticklabels(["What GDP\ncounts", "After wear\nand tear", "Carbon\ncounted", "Nature's other\ncosts, benefits"],
                                     fontsize=12, fontweight="bold", color=INK)
ax.set_xlim(-0.75, 3.75); ax.set_ylim(-50, 600)
ax.set_yticks([0, 200, 400, 600]); ax.set_yticklabels(["$0", "$200B", "$400B", "$600B"])
frame(ax)

# ---------------- 2. misunderstood ----------------
ax = fig.add_subplot(gs[0, 1])
head(ax, "MISUNDERSTOOD", FOREST, "The U.S. buys more wood products than it sells", "Imports minus exports, $B a year (below zero is a surplus)")
ax.axhline(0, color=INK, lw=0.9)
ax.plot(ag.year, ag.net, color=FARM, lw=3, zorder=2); ax.plot(sf.year, sf.net, color=SEA, lw=3, zorder=3); ax.plot(fp.year, fp.net, color=FOREST, lw=4, zorder=4)
ax.scatter([ag.year.iloc[-1]], [ag.net.iloc[-1]], color=FARM, s=50, zorder=5)
ax.text(2026.8, 46, f"Farm goods\n{usd(ag.net.iloc[-1])}", color=FARM, fontsize=13, fontweight="bold", va="center", linespacing=1.1)
ax.scatter([sf.year.iloc[-1]], [sf.net.iloc[-1]], color=SEA, s=50, zorder=5)
ax.scatter([fp.year.iloc[-1]], [fp.net.iloc[-1]], color=FOREST, s=60, zorder=5)
ax.text(2026.8, 26, f"Seafood\n{usd(sf.net.iloc[-1])}", color=SEA, fontsize=13, fontweight="bold", va="center", linespacing=1.1)
ax.text(2026.8, 4, f"Wood, pulp\nand paper\n{usd(fp.net.iloc[-1])}", color=FOREST, fontsize=13, fontweight="bold", va="center", linespacing=1.1)
ax.text(1983, 60, f"Wood trade deficit in {n_def} of {n_yr} years. When U.S.\nharvests fell in the 1990s, most of the wood\nwas cut elsewhere instead", fontsize=12, color=FOREST,
        fontweight="bold", va="top", linespacing=1.2)
ax.set_xlim(1981, 2038); ax.set_ylim(-32, 62); ax.set_xticks([1985, 1995, 2005, 2015, 2025]); ax.spines["bottom"].set_bounds(1981, 2025.5)
ax.set_yticks([-20, 0, 20, 40]); ax.set_yticklabels(["\u2212$20B", "$0", "$20B", "$40B"])
frame(ax)

# ---------------- 3. at risk ----------------
ax = fig.add_subplot(gs[1, 0])
head(ax, "AT RISK", RISK, "Forests absorb carbon, but the sink is shrinking",
     r"Carbon dioxide stored (above zero) or released (below), million tons a year")
s90, s23 = sink.net_uptake_mmt_co2e.iloc[0], sink.net_uptake_mmt_co2e.iloc[-1]
trend70 = s23 + (s23 - s90) / (2023 - 1990) * (2070 - 2023)
hi_lo, hi_hi = s23 * 1.15, s23 * 1.25
yrs = [2023, 2070]
ax.fill_between(yrs, [s23, hi_lo], [s23, hi_hi], color=FOREST, alpha=0.25, lw=0)
ax.plot(yrs, [s23, (hi_lo + hi_hi) / 2], color=FOREST, lw=3, ls=(0, (5, 3)))
ax.plot(yrs, [s23, trend70], color=RISK, lw=3, ls=(0, (5, 3)))
ax.plot(sink.year, sink.net_uptake_mmt_co2e, color=INK, lw=4, zorder=4)
ax.text(1992, s90 + 25, f"{s90:,.0f}", fontsize=13, fontweight="bold", color=INK, ha="left", va="bottom")
ax.text(2023, s23 - 90, f"{s23:,.0f}", fontsize=13, fontweight="bold", color=INK, ha="center", va="top")
ax.text(2072, (hi_lo + hi_hi) / 2 + 10, "Better\nmanagement", fontsize=13, fontweight="bold", color=FOREST, va="center", linespacing=1.1)
ax.text(2072, trend70 - 20, "Decline\ncontinues", fontsize=13, fontweight="bold", color=RISK, va="center", linespacing=1.1)
gap = (hi_lo - trend70) * 0.12
ax.annotate("", xy=(2069, hi_lo - 25), xytext=(2069, trend70 + 25), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.4))
ax.text(2068, trend70 - 90, f"Gap by 2070:\n${gap:.0f}B a year", fontsize=13, fontweight="bold", color=INK, ha="right",
        va="top", linespacing=1.1)
ax.axhline(0, color=INK, lw=0.9)
ax.scatter([2022], [farm_ghg], color=FARM, s=80, zorder=5)
ax.text(2025, farm_ghg, f"Farms release {-farm_ghg:,.0f} (2022)", color=FARM, fontsize=13, fontweight="bold", va="center")
fe = sc.loc["fleet_emissions", "central"]
ax.scatter([2023], [-fe], color=SEA, s=70, zorder=5)
ax.text(2025, -fe - 110, f"Fishing fleet releases about {fe:.0f}*", color=SEA, fontsize=13, fontweight="bold", va="center")
ax.text(2048, 1270, "after 2023: illustrative paths, not forecasts", fontsize=11, color=FAINT, ha="center", style="italic")
ax.set_xlim(1988, 2092); ax.set_ylim(-850, 1350); ax.set_xticks([1990, 2010, 2030, 2050, 2070]); ax.spines["bottom"].set_bounds(1988, 2070.5)
ax.set_yticks([-400, 0, 400, 800, 1200]); ax.set_yticklabels(["\u2212400", "0", "400", "800", "1,200"])
frame(ax)

# ---------------- 4. underinvested ----------------
ax = fig.add_subplot(gs[1, 1])
head(ax, "UNDERINVESTED", FOREST, "Forest research gets a seventh of farm research",
     "Federal formula funds to university research, fiscal 2024")
bars = [("Farms", fund["Hatch"], FARM), ("Seafood", fund["Sea Grant core plus aquaculture"], SEA),
        ("Forests", fund["McIntire-Stennis"], FOREST)]
for i, (lab, v, c) in enumerate(bars):
    ax.barh(2 - i, v, color=c, height=0.62)
    ax.text(v + 6, 2 - i, f"${v:.0f}M", va="center", fontsize=16, fontweight="bold", color=c)
ax.set_yticks([2, 1, 0]); ax.set_yticklabels([b[0] for b in bars], fontsize=14, fontweight="bold", color=INK)
ax.set_xlim(0, 320); ax.set_xticks([]); ax.set_ylim(-0.6, 2.6)
for s in ("top", "right", "bottom"): ax.spines[s].set_visible(False)
ax.spines["left"].set_color(INK); ax.tick_params(length=0)

fig.text(0.04, 0.025, "Bars in the first panel are ranges. Carbon is valued at $120 a ton ($51 to $190). Clean air covers all U.S. trees. Water and recreation cover national forests only.\n"
         "*Seafood estimates are rough. Fleet fuel emissions use a global intensity (Parker et al. 2018), and lost fishing income is scaled from the World Bank's Sunken Billions.\n"
         "EPA's inventory begins in 1990. Sources: BEA, EPA, FAO, UN Comtrade, USDA, NOAA, Cavender-Bares et al. (2022), Daigneault et al. (2024).\n"
         "Methods and data: github.com/holoros/conversation-forest-value. Chart: Weiskittel, Daigneault and Woodall, University of Maine.",
         fontsize=10, color=FAINT, va="bottom", linespacing=1.35)

fig.savefig(out + ".png", dpi=300, facecolor="white")
fig.savefig(out + ".pdf", facecolor="white")
print(f"forest {[round(v) for v in forest]} range {round(forest_lo[3])} to {round(forest_hi[3])}; farm {[round(v) for v in farm]}; "
      f"forest deficit years {n_def}/{n_yr}; trend70 {trend70:.0f}; gap ${gap:.0f}B")
