#!/usr/bin/env python3
from matplotlib import pyplot as plt
from matplotlib.patches import Patch
from matplotlib.colors import to_rgb
import numpy as np
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.transforms import offset_copy
from scipy.ndimage import gaussian_filter
from cycler import cycler
import matplotlib as mpl
import json

def to_time(t, _):
    m = int(t / 60)
    s = int(t) % 60
    return f"{m:02d}:{s:02d}"

FILES = [
    ("Mixed city", "out_mixed.json", (0, 0)),
    ("Isolated city", "out_isolated.json", (1, 0)),
    ("Community city", "out_community.json", (0, 1)),
    ("Shy city", "out_shy.json", (1, 1)),
]

COLORS = ['tab:blue', 'tab:red', 'tab:green', 'gold', 'deepskyblue', 'violet']

mpl.rcParams['hatch.linewidth'] = 2.0
fig, axes = plt.subplots(2, 2)
fig.set_size_inches(20, 11)
fig.suptitle("Heatmaps", fontsize=42)

for title, filename, coords in FILES:
    ax = axes[*coords]
    ax.set_title(title)

    try:
        with open(filename) as file:
            data = json.load(file)
    except FileNotFoundError:
        continue

    last_values = data["last_values"]
    if not last_values:
        continue
    sorted_trivias = [t for t, v in sorted(last_values.items(), key=lambda o: -o[1])]
    highscore = sorted_trivias[:6]

    cycle = cycler(color=COLORS)
    legend = []

    old_heatmaps = [np.array(data["heatmap"][trivia], dtype=float) for trivia in highscore]
    total_heatmap = np.ones(old_heatmaps[0].shape, dtype=float) * 1e-6

    for heatmap in old_heatmaps:
        total_heatmap += heatmap
        
    heatmaps = []
    for heatmap in old_heatmaps:
        heatmap /= total_heatmap
        heatmap = np.kron(heatmap, np.ones((3, 3), dtype=float))
        heatmap = gaussian_filter(heatmap, sigma=2)
        heatmaps.append(np.flipud(heatmap))
        
    for params, (index, trivia) in zip(cycle, enumerate(highscore, start=1)):
        legend.append(Patch(facecolor=params["color"], label=f"{index}. {trivia}"))
        
    LEVELS = [
        (0.1, 0.2, "."),
        (0.2, 0.4, ".."),
        (0.4, 1.0, "o"),
        #(0.0, 0.0, "/"),
    ]

    colorz = (0, 0, 0 ,0)
    for a, b, h in LEVELS:
        for params, heatmap, trivia in zip(cycle, heatmaps, highscore):
            color = to_rgb(params["color"]) + (1,)
            mask = (heatmap > a) & (heatmap <= b)
            ma = np.ma.masked_array(heatmap, ~mask)
            cmap = LinearSegmentedColormap.from_list("", [colorz, colorz])
            ax.pcolor(ma, linewidth=0, color=color, cmap=cmap, hatch=h)

    ax.set_facecolor("#888")
    ax.set_xticks([])
    ax.set_yticks([])
    ax.legend(
        handles=legend,
        bbox_to_anchor=(0.5, 0.0),
        loc='upper center',
        ncol=3,
    )

fig.savefig("heatmap.png")