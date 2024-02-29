from math import ceil
from typing import NamedTuple
import pyglet
from pyglet.gl import gl
from pyglet.math import Mat4
from pyglet.window import Window, key
from pyglet.graphics import Batch, Group

from recomm_town.common import Vec
from recomm_town.human import Human
from recomm_town.shaders.human_group import HumanGroup


class GuiGroup(Group):
    def __init__(self, window: Window, order: int = 0, parent=None):
        super().__init__(order, parent)
        self._window = window

    def set_state(self):
        h = self._window.height
        self._old_view = self._window.view
        self._window.view = Mat4().translate((0, h, 0.0))

    def unset_state(self):
        self._window.view = self._old_view


class CellRange(NamedTuple):
    w: int
    h: int
    x: int
    y: int


class App(Window):
    batch: Batch
    town_group: Group
    people_group: Group
    gui_group: GuiGroup

    _zoom: float

    def __init__(self, world):
        config = pyglet.gl.Config(alpha_size=8, samples=4)
        super().__init__(config=config, resizable=True)
        self.batch = Batch()
        self.town_group = Group(order=0)
        self.people_group = Group(order=1)
        self.gui_group = GuiGroup(self, order=2)
        self.move_position = Vec(0.0, 0.0)
        self.cell_range = CellRange(0, 0, 0, 0)
        self.set_view(Vec(0.0, 0.0))
        self.world = world
        self.place_index = 0
        self.human_index = 0
        self.tracked_human = None

    def set_view(self, position, zoom=1.0):
        self.camera_position = position
        self.camera_zoom = zoom
        self.recreate_view()

    def recreate_view(self):
        wh = self.width / 2
        hh = self.height / 2
        z = self.camera_zoom * hh / 4000.0
        p = self.camera_position * -z + Vec(wh, hh)
        view = Mat4()
        view = view.translate((p.x, p.y, 0.0))
        view = view.scale((z, z, 1.0))
        self.view = view

        is_changed = self.update_cells_range(wh, hh, z)

        if z < 0.2:
            self.people_group.visible = False
            return
        if not self.people_group.visible:
            self.people_group.visible = True
        if not is_changed:
            return

        human_groups = self.batch.group_children.get(self.people_group, [])
        for group in human_groups:
            if not isinstance(group, HumanGroup):
                continue 
            self._update_group_visible(group)

    def update_cells_range(self, wh, hh, z) -> bool:
        cell_size = HumanGroup.CELL_SIZE
        cell_range = CellRange(
            w=ceil(((wh / cell_size) + 1) / z),
            h=ceil(((hh / cell_size) + 1) / z),
            x=int(self.camera_position.x / cell_size),
            y=int(self.camera_position.y / cell_size),
        )
        is_changed = cell_range != self.cell_range
        self.cell_range = cell_range
        return is_changed

    def _update_group_visible(self, group):
        wz, hz, px, py = self.cell_range
        x = abs(px - group.cell_x)
        y = abs(py - group.cell_y)
        if x <= wz and y <= hz:
            group.visible = True
        else:
            group.visible = False

    def run(self):
        pyglet.app.run()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.Q:
            places = self.world.town.places
            position = places[self.place_index].position
            self._stop_tracking()
            self.set_view(position, zoom=8.0)
            self.place_index += 1
            if self.place_index >= len(places):
                self.place_index = 0
        if symbol == key.W:
            human = self.world.people[self.human_index]
            self._start_tracking(human)
            self.set_view(human.position, zoom=8.0)
            self.human_index += 1
            if self.human_index >= len(self.world.people):
                self.human_index = 0
        if symbol == key.UP:
            self.move_position += Vec(0.0, +20.0)
        elif symbol == key.DOWN:
            self.move_position += Vec(0.0, -20.0)
        elif symbol == key.LEFT:
            self.move_position += Vec(-20.0, 0.0)
        elif symbol == key.RIGHT:
            self.move_position += Vec(+20.0, 0.0)
        else:
            return super().on_key_press(symbol, modifiers)

    def on_key_release(self, symbol, modifiers):
        if symbol == key.UP:
            self.move_position -= Vec(0.0, +20.0)
            self._stop_tracking()
            self.recreate_view()
        elif symbol == key.DOWN:
            self.move_position -= Vec(0.0, -20.0)
            self._stop_tracking()
            self.recreate_view()
        elif symbol == key.LEFT:
            self.move_position -= Vec(-20.0, 0.0)
            self._stop_tracking()
            self.recreate_view()
        elif symbol == key.RIGHT:
            self.move_position -= Vec(+20.0, 0.0)
            self._stop_tracking()
            self.recreate_view()
        else:
            return super().on_key_press(symbol, modifiers)

    def _stop_tracking(self):
        if self.tracked_human:
            self.tracked_human.position_observers.pop("track", None)
            self.tracked_human = None

    def _start_tracking(self, human: Human):
        self._stop_tracking()
        self.tracked_human = human
        self.tracked_human.position_observers["track"] = self._track_human

    def _track_human(self, human, _):
        self.camera_position = human.position
        self.recreate_view()

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        zoom = 1.05 if scroll_y > 0 else 0.95
        self.camera_zoom *= zoom
        self.recreate_view()

    def on_resize(self, width, height):
        super().on_resize(width, height)
        self.recreate_view()

    def on_draw(self):
        self.clear()
        gl.glClearColor(0.1, 0.5, 0.1, 1.0)
        self.batch.draw()

    def on_refresh(self, dt):
        self.world.do_it(dt)
        if getattr(self.people_group, "cell_changed", False):
            self.people_group.cell_changed = False
            human_groups = self.batch.group_children.get(self.people_group, [])
            for group in human_groups:
                if not isinstance(group, HumanGroup):
                    continue 
                if group.cell_changed:
                    self._update_group_visible(group)
                    group.cell_changed = False
        if self.move_position.length_squared() > 1.0:
            self.camera_position += self.move_position
            self.recreate_view()
        
