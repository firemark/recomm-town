#!/usr/bin/env python3
from matplotlib import pyplot as plt
from matplotlib.ticker import EngFormatter, FuncFormatter
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

fig, axes = plt.subplots(2, 2)
fig.set_size_inches(16, 9)
fig.tight_layout()

for title, filename, coords in FILES:
    ax = axes[*coords]
    ax.set_title(title)

    try:
        with open(filename) as file:
            data = json.load(file)
    except FileNotFoundError:
        continue

    sorted_trivias = [t for t, v in sorted(data["last_values"].items(), key=lambda o: -o[1])]
    highscore = sorted_trivias[:10]

    for index, trivia in enumerate(highscore, start=1):
        plot = data["plot"][trivia]
        label = f"{index:}. {trivia}"
        x = [p[0] for p in plot]
        y = [p[1] * 100 for p in plot]
        ax.plot(x, y, label=label)

    ax.legend()
    ax.grid(alpha=0.50, which="major")
    ax.get_yaxis().set_major_formatter(EngFormatter())
    ax.get_xaxis().set_major_formatter(FuncFormatter(to_time))

fig.savefig("output.png")