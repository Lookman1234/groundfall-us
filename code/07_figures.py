#!/usr/bin/env python3
"""Step 7: figures and headline numbers.

Plain-language note: draws the dataset's figures into paper/figures/ and writes the
headline numbers into paper/stats.json. Figures carry a DRAFT stamp until you have
verified the data; run with --final after verification to remove it.

Figures:
  fig1_injury_rate_by_year.png    ground-failure injury rate per 200,000 hours, by
                                  sector and mine type, 2000-2025 (small multiples)
  fig2_surface_mnm_failure_modes.png   failure modes of surface M/NM ground failures
"""

import argparse

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from common import PAPER, PROC, write_stats

INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e4e3df", "#fcfcfb"
SERIES = {("coal", "underground"): "#2a78d6", ("coal", "surface"): "#eb6834",
          ("metal_nonmetal", "underground"): "#1baf7a", ("metal_nonmetal", "surface"): "#eda100"}
LABEL = {("coal", "underground"): "Coal, underground", ("coal", "surface"): "Coal, surface",
         ("metal_nonmetal", "underground"): "Metal/nonmetal, underground",
         ("metal_nonmetal", "surface"): "Metal/nonmetal, surface"}


def style(ax):
    ax.set_facecolor(SURF)
    for s in ["top", "right"]:
        ax.spines[s].set_visible(False)
    for s in ["left", "bottom"]:
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=9, length=0)
    ax.grid(axis="y", color=GRID, linewidth=0.8)
    ax.set_axisbelow(True)


def stamp(fig, final):
    if not final:
        fig.text(0.99, 0.01, "DRAFT - not yet verified", ha="right", va="bottom",
                 fontsize=9, color="#b42318", weight="bold")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--final", action="store_true")
    a = ap.parse_args()
    out = PAPER / "figures"
    out.mkdir(parents=True, exist_ok=True)

    r = pd.read_csv(PROC / "groundfall_rates.csv")
    full = r[~r["partial_year"]]
    g = (full[full["mine_type"].isin(["surface", "underground"])]
         .groupby(["year", "sector", "mine_type"])[["gf_injury", "gf_fatal", "hours"]].sum().reset_index())
    g["rate"] = g["gf_injury"] / g["hours"] * 200000
    y0, y1 = int(g["year"].min()), int(g["year"].max())

    # Figure 1: small multiples, one per sector x mine type, own y-scale (labelled)
    fig, axes = plt.subplots(2, 2, figsize=(10, 6.4), facecolor=SURF)
    stats = {}
    for ax, key in zip(axes.flat, SERIES):
        d = g[(g["sector"] == key[0]) & (g["mine_type"] == key[1])].sort_values("year")
        style(ax)
        ax.plot(d["year"], d["rate"], color=SERIES[key], linewidth=2)
        ax.scatter(d["year"].iloc[[0, -1]], d["rate"].iloc[[0, -1]], s=36, color=SERIES[key],
                   edgecolor=SURF, linewidth=2, zorder=3)
        ax.annotate(f"{d['rate'].iloc[0]:.3f}", (d["year"].iloc[0], d["rate"].iloc[0]),
                    textcoords="offset points", xytext=(0, 9), ha="left", fontsize=9, color=INK)
        ax.annotate(f"{d['rate'].iloc[-1]:.3f}", (d["year"].iloc[-1], d["rate"].iloc[-1]),
                    textcoords="offset points", xytext=(7, 0), ha="left", va="center", fontsize=9, color=INK)
        ax.text(0.99, 0.97, f"{int(d['gf_injury'].sum()):,} injuries, {int(d['gf_fatal'].sum())} deaths",
                transform=ax.transAxes, ha="right", va="top", fontsize=8.5, color=INK2)
        ax.set_title(LABEL[key], loc="left", fontsize=10.5, color=INK, weight="bold")
        ax.set_ylim(0, max(d["rate"].max() * 1.25, 0.01))
        ax.set_xlim(y0 - 0.5, y1 + 3.5)
        ax.set_xticks([2000, 2005, 2010, 2015, 2020, 2025])
        tag = f"{key[0]}_{key[1]}"
        stats[f"rate_{tag}_{y0}"] = round(float(d["rate"].iloc[0]), 4)
        stats[f"rate_{tag}_{y1}"] = round(float(d["rate"].iloc[-1]), 4)
        stats[f"injuries_{tag}_{y0}_{y1}"] = int(d["gf_injury"].sum())
        stats[f"fatal_{tag}_{y0}_{y1}"] = int(d["gf_fatal"].sum())
    fig.suptitle(f"Ground-failure injuries per 200,000 hours worked, U.S. mines, {y0}-{y1}",
                 x=0.01, ha="left", fontsize=12.5, color=INK, weight="bold")
    fig.text(0.01, 0.935, "Mine-operator employees; each panel has its own scale. "
             "Source: MSHA Accidents and Employment/Production files (2026-10-09 refresh); GroundFall-US.",
             fontsize=8.5, color=INK2)
    stamp(fig, a.final)
    fig.tight_layout(rect=(0, 0.02, 1, 0.93))
    fig.savefig(out / "fig1_injury_rate_by_year.png", dpi=200, facecolor=SURF)
    plt.close(fig)

    # Figure 2: failure modes, surface M/NM (single hue, sorted bars, direct labels)
    m = pd.read_csv(PROC / "groundfall_failure_modes.csv")
    order = m["failure_mode"].value_counts().sort_values()
    names = {k: k.replace("_", " ").capitalize() for k in order.index}
    fig, ax = plt.subplots(figsize=(8, 4.2), facecolor=SURF)
    style(ax)
    ax.grid(False)
    ax.barh([names[k] for k in order.index], order.values, color="#2a78d6", height=0.6)
    for i, v in enumerate(order.values):
        ax.text(v + 0.6, i, str(v), va="center", fontsize=9, color=INK)
    ax.set_xticks([])
    ax.spines["bottom"].set_visible(False)
    fig.suptitle(f"Failure modes of surface metal/nonmetal ground failures, {y0}-2026 (n = {len(m)})",
                 x=0.01, ha="left", fontsize=11.5, color=INK, weight="bold")
    fig.text(0.01, 0.01, f"Rule-based labels from narratives, rules v{m['rules_version'].iloc[0]}; "
             "not yet validated against hand labels.", fontsize=8.5, color=INK2)
    stamp(fig, a.final)
    fig.tight_layout(rect=(0, 0.05, 1, 0.94))
    fig.savefig(out / "fig2_surface_mnm_failure_modes.png", dpi=200, facecolor=SURF)
    plt.close(fig)

    write_stats(stats)
    print(f"Figures written to {out}")


if __name__ == "__main__":
    main()
