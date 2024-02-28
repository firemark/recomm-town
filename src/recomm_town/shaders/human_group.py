from pyglet.window import Window
from pyglet.graphics import Group

from recomm_town.human import Human


class HumanGroup(Group):
    CELL_SIZE = 200
    x: float
    y: float
    cell_x: int
    cell_y: int

    def __init__(self, window: Window, index: int, human: Human, parent: Group):
        super().__init__(index, parent)
        self._window = window
        self.x = human.position.x
        self.y = human.position.y
        self.cell_x = int(self.x / self.CELL_SIZE)
        self.cell_y = int(self.y / self.CELL_SIZE)
        self.cell_changed = True
        self.parent.cell_changed = True

    def update(self, human: Human, _):
        self.x = human.position.x
        self.y = human.position.y

        old_cell_x = self.cell_x
        old_cell_y = self.cell_y
        self.cell_x = int(self.x / self.CELL_SIZE)
        self.cell_y = int(self.y / self.CELL_SIZE)
        is_changed = old_cell_x != self.cell_x or old_cell_y != self.cell_y
        self.parent.cell_changed = self.parent.cell_changed or is_changed
        self.cell_changed = self.cell_changed or is_changed

    def set_state(self):
        self._old_view = self._window.view
        self._window.view = self._window.view.translate((self.x, self.y, 0.0))

    def unset_state(self):
        self._window.view = self._old_view
