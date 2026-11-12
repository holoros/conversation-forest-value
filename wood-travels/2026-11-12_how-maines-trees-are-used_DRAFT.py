# How Maine's trees are used, rebuilt November 12, 2026, in Python so the right panel shows tons, not shares
# (Adam Daigneault's request: stacked totals show the falling harvest).
# Data: 2009-2023_maine-wood-flow-by-product-mfs_DATA.csv, compiled from Maine Forest Service Wood Processor Reports
# (source URL per row in the file). Usage: python3 <script> <out.png>
import csv, os, sys
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
plt.rcParams["font.family"] = "Liberation Sans"
PAL = {"Sawlogs": "#1F4D33", "Pulpwood": "#3B6E8F", "Biomass Chips": "#C8873F", "Firewood/Pellets": "#A8422A"}
NAME = {"Sawlogs": "Sawlogs", "Pulpwood": "Pulpwood", "Biomass Chips": "Biomass chips", "Firewood/Pellets": "Firewood & pellets"}
USE = {"Sawlogs": "lumber, studs, veneer, pallets", "Pulpwood": "paper, pulp, tissue, packaging",
       "Biomass Chips": "electricity and heat at mills", "Firewood/Pellets": "home heating"}
BG, INK, MUT, HEAD = "#FFFFFF", "#1A1A1A", "#5B6B60", "#1A1A1A"
rows = [r for r in csv.DictReader(open(os.path.join(HERE, "2009-2023_maine-wood-flow-by-product-mfs_DATA.csv"))) if r["product"] != "Total"]
years = sorted({int(r["year"]) for r in rows})
H = {p: np.array([next(float(r["harvested_gt"]) for r in rows if int(r["year"]) == y and r["product"] == p) for y in years]) / 1e6 for p in PAL}
tot = sum(H.values())
t11, t23 = tot[years.index(2011)], tot[years.index(2023)]
assert abs(t23 - 9.996609) < 0.001 and abs(t11 - 13.5) < 0.06, (t11, t23)
r23 = {r["product"]: r for r in rows if int(r["year"]) == 2023}
exp_share = sum(float(r["exported_gt"]) for r in r23.values()) / (t23 * 1e6)
assert abs(exp_share - 0.201) < 0.002
drop = round(100 * (1 - t23 / t11))
sh = lambda p, y: 100 * H[p][years.index(y)] / tot[years.index(y)]

fig = plt.figure(figsize=(13, 6.3), dpi=300, facecolor=BG)
fig.text(0.027, 0.925, "A fifth of Maine's harvest leaves the state as raw wood", fontsize=24, fontweight="bold", color=HEAD, va="center")
fig.text(0.027, 0.862, f"Maine landowners harvested {t23:.1f} million green tons of wood in 2023, down {drop}% from {t11:.1f} million in 2011, and pulpwood's share fell from {sh('Pulpwood', 2011):.0f}% to {sh('Pulpwood', 2023):.0f}%.",
         fontsize=12.6, color="#444444", va="center")

# ---- left: the 2023 harvest, kept and exported ----
a = fig.add_axes([0.205, 0.07, 0.355, 0.63], facecolor="#FAFAF8")
order = ["Firewood/Pellets", "Biomass Chips", "Pulpwood", "Sawlogs"]
for i, p in enumerate(order):
    ins, ex = float(r23[p]["instate_gt"]) / 1e6, float(r23[p]["exported_gt"]) / 1e6
    a.barh(i, ins, color=PAL[p], height=0.62)
    a.barh(i, ex, left=ins, color=PAL[p], alpha=0.38, height=0.62)
    h = ins + ex
    a.text(h + 0.08, i + 0.10, f"{h:.1f} M tons  ·  {100 * h / t23:.0f}% of harvest", fontsize=11.6, fontweight="bold", color=INK, va="center")
    a.text(h + 0.08, i - 0.12, f"{100 * ex / h:.0f}% exported", fontsize=11.2, color=MUT, va="center")
    a.text(-0.16, i + 0.10, NAME[p], fontsize=12, fontweight="bold", color=INK, ha="right", va="center")
    a.text(-0.16, i - 0.13, USE[p], fontsize=12, fontweight="bold", color=INK, ha="right", va="center")
a.set_xlim(0, 7.4); a.set_ylim(-0.6, 3.75); a.set_yticks([]); a.set_xticks([0, 1, 2, 3, 4])
a.set_xticklabels(["0", "1", "2", "3", "4 million\ngreen tons"], fontsize=10, color=MUT)
a.grid(axis="x", color="#DED8C8", linewidth=0.5); a.set_axisbelow(True)
for s in a.spines.values(): s.set_visible(False)
a.tick_params(length=0)
fig.text(0.027, 0.79, "The 2023 harvest: 10.0 million green tons", fontsize=16, fontweight="bold", color=HEAD, va="center")
a.barh([-9], [1], color=PAL["Sawlogs"], label="Processed by Maine mills"); a.barh([-9], [1], color=PAL["Sawlogs"], alpha=0.38, label="Exported unprocessed")
a.legend(loc="lower left", bbox_to_anchor=(-0.02, 0.985), ncol=2, frameon=False, fontsize=9.6, handlelength=1, handleheight=1, columnspacing=1.2)

# ---- right: tons by product, 2009 to 2023 ----
b = fig.add_axes([0.645, 0.07, 0.185, 0.66], facecolor="white")
stack = ["Sawlogs", "Pulpwood", "Biomass Chips", "Firewood/Pellets"]
b.stackplot(years, [H[p] for p in stack], colors=[PAL[p] for p in stack], edgecolor="white", linewidth=0.5)
b.set_xlim(2009, 2023); b.set_ylim(0, 17.5); b.set_xticks([2009, 2014, 2019, 2023])
b.set_yticks([0, 5, 10, 15]); b.set_yticklabels(["0", "5", "10", "15 million\ngreen tons"], fontsize=10.5, color=MUT)
b.tick_params(length=0, labelsize=10.5, labelcolor=MUT)
for s in b.spines.values(): s.set_visible(False)
b.plot([2011, 2011], [0, t11], color="white", linewidth=1, linestyle=(0, (3, 2)))
b.text(2011, 16.3, f"2011: {t11:.1f} M", fontsize=10.6, fontweight="bold", color=MUT, ha="center", va="center")
b.plot([2011, 2011], [t11, 15.8], color=MUT, linewidth=0.6)
b.text(2023, 15.0, f"2023: {t23:.1f} M", fontsize=10.6, fontweight="bold", color=MUT, ha="right", va="center")
b.plot([2023, 2023], [t23, 14.5], color=MUT, linewidth=0.6, clip_on=False)
base = 0; lab = []
for p in stack:
    v = H[p][-1]; y = base + v / 2; base += v
    lab.append([y, p, v])
for k in range(1, len(lab)):
    lab[k][0] = max(lab[k][0], lab[k - 1][0] + 0.85)
for y, p, v in lab:
    b.text(2023.4, y, f"{NAME[p]} {v:.1f} M", fontsize=11.2, fontweight="bold", color=PAL[p], va="center", clip_on=False)
fig.text(0.60, 0.79, "Tons harvested by product, 2009 to 2023", fontsize=16, fontweight="bold", color=HEAD, va="center")
fig.savefig(sys.argv[1], dpi=300, facecolor=BG)
print("saved", round(t11, 2), round(t23, 2), drop, [round(H[p][-1], 2) for p in stack])
