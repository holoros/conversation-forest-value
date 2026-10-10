"""Forest ecosystem account figure, NYT editorial register (four panels).
Python/matplotlib sandbox render (R is not available in the sandbox); continues the Python lineage of
2026-10-04_three-gaps_plot.py. Every number is traceable to the inputs listed in SOURCES below.
Run: python3 2026-10-10_forest-gep-figure_plot.py data/us_trade_ratio_1981_2025.csv data/sector_green_nva_2022.csv <font_dir> figures/2026-10-10_forest-gep-figure_DRAFT
The sink and research fund CSVs are read from the same folder as the trade CSV. Fonts: Libre Franklin and Source Serif 4 TTFs (Google Fonts, SIL OFL);
missing fonts fall back to the default sans.
"""
import os, sys
os.environ.setdefault("MPLCONFIGDIR", "/tmp/mpl")
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
from matplotlib.gridspec import GridSpec
import pandas as pd, numpy as np, glob

trade_csv, nva_csv, font_dir, out = sys.argv[1:5]
for f in glob.glob(os.path.join(font_dir, "*.ttf")):
    fm.fontManager.addfont(f)
SANS, SERIF = "Libre Franklin", "Source Serif 4"
plt.rcParams.update({"font.family": SANS, "font.size": 12, "mathtext.fontset": "custom",
                     "mathtext.rm": SANS, "mathtext.bf": f"{SANS}:bold", "axes.unicode_minus": True, "text.parse_math": False})
import textwrap

# ---- palette: NYT editorial grammar, sector hues fixed across panels ----
INK, MUTED, FAINT, RULE, SRC = "#121212", "#3d3d3d", "#666666", "#dcdcdc", "#767676"
FOR = ["#134a31", "#2f7550", "#5f9d77", "#93c2a2", "#c4dfcb"]       # forest: GDP, carbon, air, water, recreation
AG, AG_GHOST = "#8c7d5a", "#e9e3d4"                                   # agriculture: earth tone, removed value
SEA = "#1a75b4"

# ---- data ----
nva = pd.read_csv(nva_csv).set_index("sector")
f_gdp = nva.loc["Forest", "nva"]                       # 115.2  BEA 321+322 less depreciation, 2022
f_carbon = nva.loc["Forest", "green_mid"] - f_gdp     # 92.6   771.7 MMT at $120/t
f_air = nva.loc["Forest", "full_adj_mid"]             # 42.2   Cavender-Bares et al. 2022
f_water, f_rec = 7.0, 14.0                             # Sedell et al. 2000 (inflated); USFS 2018 national forest recreation
f_tot = f_gdp + f_carbon + f_air + f_water + f_rec     # ~271
f_lo, f_hi = f_gdp + 70 + f_water + f_rec, f_gdp + 200 + f_water + f_rec   # carbon+air $70B to $200B (article range)
a_gdp = nva.loc["Agriculture", "nva"]                 # 449.4
a_ghg = a_gdp - nva.loc["Agriculture", "green_mid"]   # 71.5
a_lnw = -nva.loc["Agriculture", "full_adj_mid"]       # 183.2  FAO SOFA 2023 land, nitrogen, blue water
a_tot, a_lo, a_hi = nva.loc["Agriculture", ["full_mid", "full_lo", "full_hi"]]
s_gdp = nva.loc["Marine", "nva"]                       # 20.0   BEA MESA living resources, net

tr = pd.read_csv(trade_csv).drop_duplicates(["year", "sector"], keep="last").sort_values("year")
data_dir = os.path.dirname(os.path.abspath(trade_csv))
sink = pd.read_csv(os.path.join(data_dir, "epa_forest_sink_1990_2023.csv")).rename(columns={"net_uptake_mmt_co2e": "mmt"})   # EPA GHGI 1990-2023 Table 6-1
fund = pd.read_csv(os.path.join(data_dir, "research_capacity_funds_fy2024.csv")).set_index("program")["usd_millions"]
funds = [("Farms\nHatch", int(fund["Hatch"]), AG), ("Seafood\nSea Grant", int(fund["Sea Grant core plus aquaculture"]), SEA), ("Forests\nMcIntire-\nStennis", int(fund["McIntire-Stennis"]), FOR[0])]

usd = lambda x: f"${x:,.0f}B"

def frame(ax, left=False):
    for sp in ["top", "right", "left"]:
        ax.spines[sp].set_visible(left and sp == "left")
    ax.spines["bottom"].set_color(INK); ax.spines["bottom"].set_linewidth(0.8)
    ax.tick_params(length=0, colors=MUTED, labelsize=11); ax.set_axisbelow(True)

def ptitle(ax, t, sub, y=1.0, pm=False):
    ax.text(0, y + 0.115, t, transform=ax.transAxes, fontsize=15, fontweight="bold", color=INK, va="bottom")
    ax.text(0, y + 0.03, sub, transform=ax.transAxes, fontsize=11, color=MUTED, va="bottom", parse_math=pm)

fig = plt.figure(figsize=(32 / 2.54, 29 / 2.54), dpi=300)
fig.patch.set_facecolor("white")
gs = GridSpec(2, 2, height_ratios=[1.0, 1.05], width_ratios=[1.75, 0.75],
              hspace=0.5, wspace=0.42, left=0.045, right=0.975, top=0.735, bottom=0.245)

# ---- headline block ----
fig.text(0.045, 0.972, "U.S. forests give back roughly twice what GDP counts,", fontsize=24,
         fontweight="bold", family=SERIF, color=INK, va="top")
fig.text(0.045, 0.938, "and wood not grown here is cut somewhere else", fontsize=24,
         fontweight="bold", family=SERIF, color=INK, va="top")
fig.text(0.045, 0.898, "GDP credits forests with about $115B a year in wood and paper. Carbon, clean air, water and recreation add $90B to $220B, so GDP captures about a\n"
         "third to a half of what forests provide. The carbon sink is weakening as forests age and disturbances mount, harvest given up at home is mostly made\n"
         "up by cutting elsewhere, and forest research receives a seventh of the federal capacity funds that farm research receives.",
         fontsize=12, color=MUTED, va="top", linespacing=1.35)
# ---- Panel 1: the account ----
ax = fig.add_subplot(gs[0, :])
ptitle(ax, "1. Undervalued",
       "What the national accounts count, and what an ecosystem account adds. United States, 2022, $B a year. Forest segments add services; farm segments subtract damage.")
H = 0.56
yF, yA, yS = 2.12, 1.0, 0.0
# forest stack
segs = [("Wood and paper\n(what GDP counts)", f_gdp), ("Carbon taken up", f_carbon), ("Clean air*", f_air),
        ("Water", f_water), ("Recreation", f_rec)]
left = 0
for i, (lab, w) in enumerate(segs):
    ax.barh(yF, w, left=left, height=H, color=FOR[i], lw=0)
    if i == 0:
        ax.text(left + 6, yF, f"Wood and paper {usd(w)}\nwhat GDP counts", color="white", fontsize=11, fontweight="bold", va="center", linespacing=1.15)
    elif i in (1, 2):
        ax.text(left + w / 2, yF, f"{lab}\n{usd(w)}", color="white" if i == 1 else INK, fontsize=10.5,
                fontweight="bold", va="center", ha="center", linespacing=1.15)
    left += w
# narrow segments labeled above with leaders
ax.annotate(f"Water {usd(f_water)}", xy=(f_gdp + f_carbon + f_air + f_water / 2, yF + H / 2), xytext=(232, yF + 0.5),
            fontsize=10, fontweight="bold", color=FOR[1], ha="center", arrowprops=dict(arrowstyle="-", color=FAINT, lw=0.6))
ax.annotate(f"Recreation {usd(f_rec)}", xy=(f_tot - f_rec / 2, yF + H / 2), xytext=(300, yF + 0.5),
            fontsize=10, fontweight="bold", color=FOR[1], ha="center", arrowprops=dict(arrowstyle="-", color=FAINT, lw=0.6))
ax.text(334, yF + 0.5, "(national forests only)", fontsize=9.5, color=FAINT, ha="left", style="italic")
# forest total with range
wF = yF - H / 2 - 0.11
ax.errorbar(f_tot, wF, xerr=[[f_tot - f_lo], [f_hi - f_tot]], fmt="none", ecolor=INK, elinewidth=1.3, capsize=4, zorder=5)
ax.scatter(f_tot, wF, s=40, color=INK, zorder=6)
ax.text(f_hi + 8, wF, f"range {usd(f_lo)} to {usd(f_hi)}; wildlife habitat has no national value", fontsize=9.5, color=MUTED, va="center")
ax.text(f_tot + 12, yF + 0.05, f"Forests {usd(f_tot)}", fontsize=16, fontweight="bold", color=FOR[0], va="bottom")
# agriculture: kept value plus removed (ghost) segments
ax.barh(yA, a_tot, height=H, color=AG, lw=0)
ax.barh(yA, a_lnw, left=a_tot, height=H, color=AG_GHOST, lw=0.8, edgecolor=AG, hatch="///")
ax.barh(yA, a_ghg, left=a_tot + a_lnw, height=H, color=AG_GHOST, lw=0.8, edgecolor=AG, hatch="...")
ax.text(a_tot + a_lnw / 2, yA, f"Land, nitrogen and\nwater damage −{usd(a_lnw)}", fontsize=10.5, fontweight="bold",
        color="#5a4e32", ha="center", va="center", linespacing=1.15,
        bbox=dict(boxstyle="round,pad=0.15", fc=AG_GHOST, ec="none"))
ax.text(a_tot + a_lnw + a_ghg / 2, yA, f"Emissions\n−{usd(a_ghg)}", fontsize=9.5, fontweight="bold", color="#5a4e32",
        ha="center", va="center", linespacing=1.1, bbox=dict(boxstyle="round,pad=0.1", fc=AG_GHOST, ec="none"))
ax.plot([a_gdp, a_gdp], [yA - H / 2 - 0.06, yA + H / 2 + 0.06], color=INK, lw=1.2)
ax.text(a_gdp, yA + H / 2 + 0.09, f"What GDP counts {usd(a_gdp)}", fontsize=10.5, fontweight="bold", color=INK, ha="center")
wA = yA - H / 2 - 0.11
ax.errorbar(a_tot, wA, xerr=[[a_tot - a_lo], [a_hi - a_tot]], fmt="none", ecolor=INK, elinewidth=1.3, capsize=4, zorder=5)
ax.scatter(a_tot, wA, s=40, color=INK, zorder=6)
ax.text(a_hi + 8, wA, f"range −{usd(-a_lo)} to {usd(a_hi)}", fontsize=9.5, color=MUTED, va="center")
ax.text(8, yA, f"Agriculture {usd(a_tot)}", fontsize=16, fontweight="bold", color="white", va="center")
# seafood
ax.barh(yS, s_gdp, height=H, color=SEA, lw=0)
ax.text(s_gdp + 8, yS + 0.07, f"Seafood {usd(s_gdp)}", fontsize=15, fontweight="bold", color=SEA, va="bottom")
ax.text(s_gdp + 8, yS - 0.04, "Hidden costs not estimated for the U.S. About 80% of the seafood Americans eat is imported, so much of the\n"
        "footprint, including the feed-fish harms documented by The New York Times this month, lands abroad.",
        fontsize=10, color=MUTED, va="top", linespacing=1.25)
ax.axvline(0, color=INK, lw=0.8)
ax.set_yticks([]); ax.set_ylim(-0.6, 2.75); ax.set_xlim(-50, 600)
ax.set_xticks(range(0, 601, 100)); ax.set_xticklabels([usd(v) for v in range(0, 601, 100)])
ax.xaxis.grid(True, color=RULE, lw=0.6); frame(ax)
ax.spines["bottom"].set_visible(False)


# ---- Panel 2: misunderstood, two paths for the forest carbon sink ----
ax = fig.add_subplot(gs[1, 0])
ptitle(ax, "2. Misunderstood", r"Net carbon uptake by U.S. forests, million t CO$_2$e a year. Paths after 2023 are illustrations, not forecasts", pm=True)
y0, y1 = 2023, 2070
s23, s90 = sink.mmt.iloc[-1], sink.mmt.iloc[0]
slope = (s23 - s90) / (2023 - 1990)                      # -5.3 per year, endpoint trend
trend70 = s23 + slope * (y1 - y0)                        # ~631
hi_lo, hi_hi = s23 * 1.15, s23 * 1.25                    # Maine mixed management +15% to +25% (illustrative)
yrs = np.array([y0, y1])
ax.fill_between(yrs, [s23, hi_lo], [s23, hi_hi], color=FOR[2], alpha=0.35, lw=0)
ax.plot(yrs, [s23, hi_lo], color=FOR[0], lw=2.2); ax.plot(yrs, [s23, hi_hi], color=FOR[0], lw=2.2)
RED = "#c9333b"
ax.fill_between(yrs, [s23, 0], [s23, trend70], color=RED, alpha=0.12, lw=0)
ax.plot(yrs, [s23, trend70], color=RED, lw=2.2)
ax.plot(yrs, [s23, 0], color=RED, lw=1.6, ls=(0, (4, 3)))
ax.plot(sink.year, sink.mmt, color=INK, lw=2.4, zorder=4); ax.scatter(sink.year, sink.mmt, color=INK, s=22, zorder=5)
ax.text(1990, s90 + 60, "1,055", fontsize=11, fontweight="bold", color=INK, ha="center")
ax.text(2021, s23 - 70, "880 in 2023", fontsize=11, fontweight="bold", color=INK, ha="center", va="top")
ax.text(2006, 1210, "EPA inventory", fontsize=10, color=MUTED, ha="center")
ax.text(2072, (hi_lo + hi_hi) / 2, "Manage and invest\n+15% to +25%\n(Maine result, for scale)", fontsize=11.5, fontweight="bold", color=FOR[0], va="center", linespacing=1.15)
ax.text(2072, trend70, "Aging, crowding and\ndisturbance if the 1990\nto 2023 decline continues", fontsize=11, fontweight="bold", color=RED, va="center", linespacing=1.15)
ax.text(2072, 150, "Forest Service scenario\nwith high wood demand\nand forest loss", fontsize=10, fontweight="bold", color=RED, va="center", linespacing=1.15)
gap_mt = hi_lo - trend70; gap_lo = gap_mt * 0.12; gap_hi = hi_hi * 0.12
ax.annotate("", xy=(2066, hi_lo - 10), xytext=(2066, trend70 + 10), arrowprops=dict(arrowstyle="<->", color=INK, lw=1.2))
ax.text(2064.5, (hi_lo + trend70) / 2 + 25, f"{gap_mt:,.0f} million t apart\nby 2070, ${gap_lo:.0f}B a year", fontsize=10,
        fontweight="bold", color=INK, ha="right", va="center", linespacing=1.2)
ax.text(1990, 70, "Cutting less at home does not cut demand. When\nfederal harvests in the Pacific Northwest fell in the\n1990s, more than 80% of the lost harvest was made\nup by cutting elsewhere in North America. The U.S.\nnow imports $47B of forest products and exports $34B.",
        fontsize=10, color=MUTED, va="bottom", linespacing=1.25)
ax.axvline(2023, color=RULE, lw=1, zorder=0)
ax.set_xlim(1987, 2071); ax.set_ylim(0, 1300); ax.set_xticks([1990, 2010, 2030, 2050, 2070])
ax.set_yticks([0, 250, 500, 750, 1000, 1250]); ax.set_yticklabels(["0", "250", "500", "750", "1,000", "1,250"])
ax.yaxis.grid(True, color=RULE, lw=0.6); frame(ax)

# ---- Panel 3: underinvested ----
ax = fig.add_subplot(gs[1, 1])
ptitle(ax, "3. Underinvested", "Federal research capacity funds, FY2024")
for i, (lab, v, c) in enumerate(funds):
    ax.bar(i, v, color=c, width=0.62)
    ax.text(i, v + 6, f"${v}M", ha="center", fontsize=13, fontweight="bold", color=INK)
ax.text(2, 38 + 45, "one seventh\nof Hatch", ha="center", fontsize=10, color=FOR[0], fontweight="bold", va="bottom", linespacing=1.15)
ax.set_xticks(range(3)); ax.set_xticklabels([f[0] for f in funds], fontsize=10.5, fontweight="bold", color=INK)
ax.set_ylim(0, 300); ax.set_yticks([]); ax.set_xlim(-0.55, 2.55); frame(ax)

# ---- source block ----
src = ("Notes: Ranges are scenario ranges, not statistical confidence intervals; the national accounts publish no sampling error for value added, "
       "and EPA's annual sink uncertainty is not drawn. Panel 1: value added less depreciation (BEA 2022). Forest carbon is the 2022 net uptake "
       "(772 million t, EPA) at $51 to $190 per t (central $120); clean air from Cavender-Bares et al. (2022); water (Sedell et al. 2000, inflated) "
       "and recreation (USDA Forest Service) cover national forests only; *clean air covers all U.S. trees, including urban trees; forest carbon is net of fire and other disturbance emissions, but wildfire smoke damage is not charged; dollar years and methods are mixed and the values are welfare measures, so the total is "
       "indicative and not comparable with Bhutan's account. Agriculture is charged its own emissions and FAO (2023) estimates of land, nitrogen and water damage "
       "(range −57% to +100%). Seafood is BEA marine living resources; import share from NOAA Fisheries of the United States 2023. "
       "Panel 2: EPA inventory 1990 to 2023, forest carbon stock change including wood products, years EPA tabulates. Paths are illustrations built from "
       "published end points, not forecasts: manage and invest applies the 15% to 25% carbon gain from mixed management in Maine (Daigneault et al. 2024) "
       "to the 2023 national sink; the decline path extends the 1990 to 2023 change; the net source scenario is from the 2020 RPA Assessment (high wood demand, "
       "forest loss); EPA attributes the 1990 to 2023 decline to aging forests and rising fire and other disturbance. "
       "Leakage: Wear and Murray (2004), via Murray (2019); trade from UN Comtrade, HS 44, 47 and 48, 2024. The 2070 gap prices the distance between the manage and invest low edge and the trend path at $120 per t. "
       " Panel 3: Hatch, McIntire-Stennis, Sea Grant core plus aquaculture, FY2024 enacted. "
       "Chart: Weiskittel, Daigneault and Woodall, University of Maine.")
src = "\n".join(textwrap.wrap(src, 190))
fig.text(0.045, 0.012, src, fontsize=9, color=SRC, va="bottom", linespacing=1.3)

fig.savefig(out + ".png", dpi=300, facecolor="white")
fig.savefig(out + ".pdf", facecolor="white")
fig.savefig(out + "_thumb.png", dpi=72, facecolor="white")
print(f"forest total {f_tot:.1f} ({f_lo:.1f} to {f_hi:.1f}); ag {a_tot:.1f} ({a_lo:.1f} to {a_hi:.1f}); trend70 {trend70:.0f}; gap {gap_lo:.0f} to {gap_hi:.0f}")
