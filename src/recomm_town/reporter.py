import time
import json
from pathlib import Path
from collections import defaultdict
from functools import partial

try:
    import numpy as np
except ImportError:
    NUMPY_FOUND = False
else:
    NUMPY_FOUND = True


from recomm_town.common import Trivia, TriviaChunk, Vec
from recomm_town.human import Human


class TriviaReporter:
    MARGIN = 250.0
    HEATMAP_SIZE = 32

    start_time: float
    trivia_heatmap: defaultdict[Trivia, "np.ndarray"]
    trivia_plot: defaultdict[Trivia, list[tuple[float, float]]]

    def __init__(self, boundaries: tuple[Vec, Vec]):
        margin = self.MARGIN
        self.start_time = time.monotonic()
        self.start_position = boundaries[0] - margin
        self.size = boundaries[1] - boundaries[0] + margin * 2
        assert self.size.x > 0.0
        assert self.size.y > 0.0

        if self.size.x > self.size.y:
            ratio = self.size.y / self.size.x
            w = self.HEATMAP_SIZE
            h = int(self.HEATMAP_SIZE * ratio)
        else:
            ratio = self.size.x / self.size.y
            w = int(self.HEATMAP_SIZE * ratio)
            h = self.HEATMAP_SIZE

        self.width = w
        self.height = h
        self.trivia_plot = defaultdict(list)
        if NUMPY_FOUND:
            self.trivia_heatmap = defaultdict(lambda: np.zeros((h, w), dtype=np.uint32))

    def write(self, filename: Path | str):
        label = self._trivia_label
        with open(filename, "w") as file:
            if NUMPY_FOUND:
                heatmap = self.trivia_heatmap
            else:
                heatmap = []
            plot = self.trivia_plot
            obj = {
                "heatmap": {label(t): v.tolist() for t, v in heatmap.items()},
                "plot": {label(t): v for t, v in plot.items()},
                "last_values": {label(t): v[-1][1] for t, v in plot.items() if v},
            }
            json.dump(obj, file)

    def write_on_minute(self, filename: Path | str, match_time: int):
        if match_time % 60 == 0:
            self.write(filename)

    def register(self, people: list[Human]):
        for human in people:
            human.knowledge_observers["reporter"] = self._trivia_update

    @staticmethod
    def _trivia_label(trivia: Trivia):
        return f"[{trivia.category}] {trivia.name}"

    def _trivia_update(
        self,
        position: Vec,
        trivia_chunk: TriviaChunk,
        new_value: float,
        old_value: float,
    ):
        trivia, _ = trivia_chunk
        if NUMPY_FOUND:
            self._heatmap_update(position - self.start_position, trivia)
        self._plot_update(trivia, new_value - old_value)

    def _heatmap_update(self, position: Vec, trivia: Trivia):
        size = self.size
        width = self.width - 1
        height = self.height - 1
        heatmap_x = min(int(position.x / size.x * width), width)
        heatmap_y = min(int(position.y / size.y * height), height)
        assert heatmap_x >= 0, heatmap_x
        assert heatmap_y >= 0, heatmap_y
        heatmap = self.trivia_heatmap[trivia]
        heatmap[height - heatmap_y, heatmap_x] += 1.0

    def _plot_update(self, trivia: Trivia, diff: float):
        timestamp = time.monotonic() - self.start_time
        plot = self.trivia_plot[trivia]
        prev_value = plot[-1][1] if plot else 0.0
        current_value = max(0.0, prev_value + diff)
        plot.append((timestamp, current_value))
