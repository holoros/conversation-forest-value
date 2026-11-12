# U.S. net trade in lumber and pulp, 2004 to 2024 (exports minus imports, nominal dollars).
# Data: 2004-2024_us-lumber-and-pulp-trade-comtrade_DATA.csv (UN Comtrade public preview, reporter United States,
# partner World, HS 4407 sawn wood, 4703 chemical sulfate (kraft) pulp, 470329 bleached non-coniferous kraft pulp).
# Five reference years only; the lines connect those years and do not show the years between.
# Usage: python3 <script> <out.png>
import csv, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
plt.rcParams["font.family"] = "Liberation Sans"
INK, MUT = "#1A1A1A", "#5F6B65"
COL = {"Lumber (sawn wood)": "#1F4D33", "Hardwood kraft pulp": "#3B6E8F", "All kraft pulp": "#9AA7AE"}
NAME = {"Lumber (sawn wood)": "Lumber", "Hardwood kraft pulp": "Hardwood pulp", "All kraft pulp": "All kraft pulp"}
rows = list(csv.DictReader(open(os.path.join(HERE, "2004-2024_us-lumber-and-pulp-trade-comtrade_DATA.csv"))))
net = {}
for r in rows:
    net.setdefault(r["product"], []).append((int(r["year"]), (float(r["exports_usd"]) - float(r["imports_usd"])) / 1e9))
def usd(v):
    return ("−" if v < 0 else "+") + f"\\${abs(v):.1f}B"

fig = plt.figure(figsize=(10, 5.9), dpi=300, facecolor="white")
ax = fig.add_axes([0.07, 0.10, 0.71, 0.66])
ax.axhline(0, color=INK, linewidth=1.1, zorder=2)
ax.axhspan(-8.6, 0, color="#F6F1EC", zorder=0)
for p in ("All kraft pulp", "Hardwood kraft pulp", "Lumber (sawn wood)"):
    xs, ys = zip(*sorted(net[p]))
    ax.plot(xs, ys, color=COL[p], linewidth=3.2 if p != "All kraft pulp" else 2.4, marker="o", markersize=6.5, zorder=3, solid_capstyle="round")
    ax.text(2024.5, ys[-1], f"{NAME[p]} {usd(ys[-1])}", color=COL[p] if p != "All kraft pulp" else "#5F6B65", fontsize=12, fontweight="bold", va="center", clip_on=False)
    if p == "Lumber (sawn wood)":
        ax.text(2004.5, ys[0] + 0.05, usd(ys[0]), color=COL[p], fontsize=10.5, fontweight="bold", va="center", ha="left")
ax.text(2010.0, 2.3, "Sells more than it buys", fontsize=10.5, color=MUT, va="center")
ax.text(2010.0, -8.05, "Buys more than it sells", fontsize=10.5, color=MUT, va="center")
ax.set_xlim(2003.2, 2024.4); ax.set_ylim(-8.6, 2.8)
ax.set_xticks([2004, 2010, 2014, 2019, 2024]); ax.set_yticks([-8, -6, -4, -2, 0, 2])
ax.set_yticklabels(["−\\$8B", "−\\$6B", "−\\$4B", "−\\$2B", "0", "+\\$2B"], fontsize=10.5, color=MUT)
ax.tick_params(length=0, labelsize=10.5, labelcolor=MUT, pad=6)
ax.grid(axis="y", color="#DDDDDD", linewidth=0.6); ax.set_axisbelow(True)
for s in ax.spines.values(): s.set_visible(False)
fig.text(0.03, 0.925, "The U.S. buys more lumber and hardwood pulp than it sells", fontsize=21, fontweight="bold", color=INK, va="center")
fig.text(0.03, 0.845, "U.S. exports minus imports in five reference years, 2004 to 2024, in dollars not adjusted for inflation.\nThe country still sells more pulp overall than it buys, mostly softwood pulp.",
         fontsize=11.6, color="#444444", va="center", linespacing=1.3)
fig.savefig(sys.argv[1], dpi=300, facecolor="white")
print({k: [(y, round(v, 2)) for y, v in sorted(vv)] for k, vv in net.items()})
