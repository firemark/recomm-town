import time
import json
from pathlib import Path
from collections import defaultdict
from functools import partial

import numpy as np

from recomm_town.common import Trivia, TriviaChunk, Vec
from recomm_town.human import Human


class TriviaReporter:
    HEATMAP_WIDTH = 32
    HEATMAP_HEIGHT = 32

    start_time: float
    trivia_heatmap: defaultdict[Trivia, np.ndarray]
    trivia_plot: defaultdict[Trivia, list[tuple[float, float]]]

    def __init__(self, boundaries: tuple[Vec, Vec]):
        w = self.HEATMAP_WIDTH
        h = self.HEATMAP_HEIGHT

        self.start_time = time.monotonic()
        self.start_position = boundaries[0]
        self.size = boundaries[1] - boundaries[0] + 200.0
        assert self.size.x > 0.0
        assert self.size.y > 0.0

        self.trivia_plot = defaultdict(list)
        self.trivia_heatmap = defaultdict(lambda: np.zeros((h, w), dtype=np.uint32))
        self.people_count = 0

    def write(self, filename: Path | str):
        label = self._trivia_label
        with open(filename, "w") as file:
            heatmap = self.trivia_heatmap
            plot = self.trivia_plot
            obj = {
                "heatmap": {label(t): v.tolist() for t, v in heatmap.items()},
                "plot": {label(t): v for t, v in plot.items()},
                "last_values": {label(t): v[-1][1] for t, v in plot.items() if v},
            }
            json.dump(obj, file)

    def register(self, people: list[Human]):
        self.people_count = len(people)
        for human in people:
            human.knowledge_observers["reporter"] = partial(self._trivia_update, human)

    @staticmethod
    def _trivia_label(trivia: Trivia):
        return f"[{trivia.category}] {trivia.name}"

    def _trivia_update(
        self,
        human: Human,
        trivia_chunk: TriviaChunk,
        new_value: float,
        old_value: float,
    ):
        trivia, chunk_no = trivia_chunk
        self._heatmap_update(human, trivia)
        self._plot_update(trivia, new_value - old_value)

    def _heatmap_update(self, human: Human, trivia: Trivia):
        position = human.position - self.start_position
        size = self.size
        width = self.HEATMAP_WIDTH - 1
        height = self.HEATMAP_HEIGHT - 1
        heatmap_x = min(int(position.x / size.x * width), width)
        heatmap_y = min(int(position.y / size.y * height), height)
        assert heatmap_x >= 0
        assert heatmap_y >= 0
        heatmap = self.trivia_heatmap[trivia]
        heatmap[height - heatmap_y, heatmap_x] += 1.0

    def _plot_update(self, trivia: Trivia, diff: float):
        diff_normal = diff / (trivia.chunks * self.people_count)

        timestamp = time.monotonic() - self.start_time
        plot = self.trivia_plot[trivia]
        prev_value = plot[-1][1] if plot else 0.0
        current_value = max(0.0, prev_value + diff_normal)
        plot.append((timestamp, current_value))
