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
        w = self.width
        h = self.height
        wh = w / 2
        hh = h / 2
        z = self.camera_zoom * h / 4000.0
        p = self.camera_position * -z + Vec(wh, hh)
        view = Mat4()
        view = view.translate((p.x, p.y, 0.0))
        view = view.scale((z, z, 1.0))
        self.view = view

        return
        # TODO - dont show human outside the area
        human_groups = self.batch.group_children.get(self.people_group, [])
        wz = wh / z
        hz = hh / z
        px = self.camera_position.x
        py = self.camera_position.y

        c = 0
        for group in human_groups:
            if not isinstance(group, HumanGroup):
                continue
            x = abs(px - group.x)
            y = abs(py - group.y)
            if x < wz and y < hz:
                c += 1
                group.visible = True
            else:
                group.visible = False
        print("count", c)

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
        if self.move_position.length_squared() > 1.0:
            self.camera_position += self.move_position
            self.recreate_view()
