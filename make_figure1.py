"""Figure 1 of the Matters Arising.

Usage from the reproducibility folder of the package
    python make_figure1.py ../data source_data
"""
import os
import sys
import zipfile
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.join("..", "data")
OUT = sys.argv[2] if len(sys.argv) > 2 else "source_data"
os.makedirs(OUT, exist_ok=True)
# Unzip the nested archive with the individual records when the folder is missing
if not os.path.isdir(os.path.join(ROOT, "Datasets")):
    with zipfile.ZipFile(os.path.join(ROOT, "Datasets.zip")) as z:
        z.extractall(ROOT)
ann = pd.read_csv(f"{ROOT}/Datasets/metadata/metadata_ground_truth.csv")
gt = pd.read_csv(f"{ROOT}/metadata_gt.csv")
M = ["TRBL", "ESA", "BDG", "GP", "PV", "PRL", "WLSA", "PLR", "PES", "PIF"]
N = ["OPC", "SPC", "MVP", "PRLC", "PLF", "PDES", "APC", "MS"]
NAMES = {"TRBL": "Thick reticular lines", "ESA": "Eccentric structureless", "BDG": "Peripheral dots",
         "GP": "Grey patterns", "PV": "Polymorphous vessels", "PRL": "Pseudopods (partial)",
         "WLSA": "White lines or areas", "PIF": "Follicle invasion", "OPC": "One pattern, one color",
         "SPC": "Symmetrical combination", "PRLC": "Pseudopods (entire)", "APC": "Asymmetric combination",
         "MS": "Melanoma simulator"}
FLAGS = ["GP", "TRBL", "BDG", "ESA", "WLSA", "PV", "PRL", "PIF", "MS", "APC", "SPC", "OPC", "PRLC"]


def kappa(x, y):
    # Cohen's kappa for two binary raters
    x, y = np.asarray(x, float), np.asarray(y, float)
    po = (x == y).mean()
    pe = x.mean() * y.mean() + (1 - x.mean()) * (1 - y.mean())
    return (po - pe) / (1 - pe)


a1 = ann[ann.annotator == 1].set_index("image_id")[M + N]
pairs = ann[ann.annotator != 1].join(a1, on="image_id", rsuffix="_a1")
Y = gt.benign_malignant.to_numpy()
rows = []
for f in FLAGS:
    cls = 1 if f in M else 0
    sub = pairs[pairs.benign_malignant == cls]
    rows.append(dict(concept=f, pool="M" if cls else "N", merged_prev=100 * gt.loc[Y == cls, f].mean(),
                     k_all=kappa(pairs[f], pairs[f + "_a1"]), k_cls=kappa(sub[f], sub[f + "_a1"]),
                     obs_cls=100 * (sub[f] == sub[f + "_a1"]).mean(),
                     p_a1=100 * sub[f + "_a1"].mean(), p_oth=100 * sub[f].mean()))
d = pd.DataFrame(rows)
top5 = set(d.sort_values("merged_prev", ascending=False).concept.head(5))
d["top5"] = d.concept.isin(top5)
d.rename(columns={"k_all": "kappa_all", "k_cls": "kappa_within", "obs_cls": "observed_within",
                  "p_a1": "prev_a1", "p_oth": "prev_others"}).to_csv(f"{OUT}/figure1_source_data.csv", index=False)

sns.set_theme(style="whitegrid", context="paper", font="DejaVu Sans",
              rc={"font.size": 9, "axes.labelsize": 9, "xtick.labelsize": 8.5, "ytick.labelsize": 9,
                  "legend.fontsize": 8, "axes.edgecolor": "0.3", "grid.color": "0.88"})
pal = sns.color_palette("deep")
col = {"M": pal[3], "N": pal[0]}
d["y"] = np.arange(len(d))[::-1]
pc = [col[p] for p in d.pool]
fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(6.6, 4.8), sharey=True,
                                    gridspec_kw={"width_ratios": [1.15, 0.85, 1.0]})
for r in d.itertuples():
    ax1.plot([r.k_cls, r.k_all], [r.y, r.y], color="0.7", lw=1.6, zorder=1)
    ax3.plot([r.p_oth, r.p_a1], [r.y, r.y], color="0.7", lw=1.6, zorder=1)
sns.scatterplot(x=d.k_all, y=d.y, ax=ax1, s=40, facecolor="white", edgecolor=pc, linewidth=1.4, zorder=2, label="All pairs")
sns.scatterplot(x=d.k_cls, y=d.y, ax=ax1, s=40, color=pc, edgecolor="white", linewidth=0.4, zorder=3, label="Pairs within class")
sns.scatterplot(x=d.obs_cls, y=d.y, ax=ax2, s=40, color=pc, edgecolor="white", linewidth=0.4, zorder=3, label="Pairs within class")
sns.scatterplot(x=d.p_oth, y=d.y, ax=ax3, s=38, marker="s", color="0.35", edgecolor="white", linewidth=0.4, zorder=2, label="Annotators 2 to 14")
sns.scatterplot(x=d.p_a1, y=d.y, ax=ax3, s=40, color=pc, edgecolor="white", linewidth=0.4, zorder=3, label="Annotator 1")
ax1.set_yticks(d.y)
ax1.set_yticklabels([NAMES[f] for f in d.concept])
for t, p, b in zip(ax1.get_yticklabels(), d.pool, d.top5):
    t.set_color(col[p])
    t.set_fontweight("bold" if b else "normal")
ax1.axvline(0, color="0.4", lw=0.8, ls=":")
ax1.text(0.005, -1.05, "chance", fontsize=7.5, color="0.35", ha="left", va="center")
ax1.set_xlim(-0.04, 0.56)
ax1.set_xticks([0, 0.2, 0.4])
ax1.set_xticks([0.1, 0.3, 0.5], minor=True)
ax1.grid(axis="x", which="minor", color="0.93", lw=0.6)
ax1.tick_params(axis="x", which="minor", length=0)
ax1.set_xlabel("Cohen's kappa")
ax2.set_xlim(0, 100)
ax2.set_xticks([0, 25, 50, 75, 100])
ax2.set_xlabel("Observed agreement (%)")
ax3.set_xlim(-4, 104)
ax3.set_xticks([0, 25, 50, 75, 100])
ax3.set_xlabel("Prevalence (%)")
for ax in (ax1, ax2, ax3):
    ax.set_ylabel("")
    ax.set_ylim(-1.6, len(d) - 0.4)
    ax.grid(axis="y", visible=False)
    ax.legend(frameon=False, loc="lower left", bbox_to_anchor=(-0.03, 1.0), ncol=1, handletextpad=0.2, borderaxespad=0.2)
    for h in ax.get_legend().legend_handles:
        h.set_edgecolor("0.3")
    sns.despine(ax=ax, left=True)
ax1.get_legend().legend_handles[0].set_facecolor("white")
ax1.get_legend().legend_handles[1].set_facecolor("0.3")
ax2.get_legend().legend_handles[0].set_facecolor("0.3")
ax3.get_legend().legend_handles[1].set_facecolor("0.3")
for ax, lab in [(ax1, "a)"), (ax2, "b)"), (ax3, "c)")]:
    ax.text(-0.02, 1.13, lab, transform=ax.transAxes, fontweight="bold", fontsize=11, ha="right", va="bottom")
fig.tight_layout(w_pad=0.8)
for ext in ("pdf", "png", "jpg"):
    fig.savefig(f"{OUT}/figure1.{ext}", dpi=600 if ext != "pdf" else None, bbox_inches="tight")
print(d.round(3).to_string(index=False))
