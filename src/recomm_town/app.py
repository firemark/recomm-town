from math import ceil
from queue import Empty, Queue
from typing import Literal, NamedTuple
import pyglet
from pyglet.gl import gl
from pyglet.math import Mat4
from pyglet.window import Window, key
from pyglet.graphics import Batch, Group
from pyglet.image import load as image_load

from recomm_town.common import Vec
from recomm_town.human import Human
from recomm_town.observer import Observer
from recomm_town.shaders.human_group import HumanGroup

SPECIAL_A = 0xad00000000
SPECIAL_B = 0xac00000000
SPECIAL_C = 0xab00000000
SPECIAL_D = 0x7900000000 
SPECIAL_UP = 0x7b00000000
SPECIAL_DOWN = 0x7a00000000


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
    label_group: Group
    people_group: Group
    gui_group: GuiGroup

    _zoom: float
    _page: Literal['world', 'graph', 'heatmap']

    def __init__(self, world, queue: Queue, match_time: int = 600):
        #config = pyglet.gl.Config(alpha_size=8, samples=4)
        config = pyglet.gl.Config(opengl_api="gl")
        super().__init__(config=config, resizable=True)

        self._page = 'world'
        self._page_image = None
        self._page_timer = None

        self.set_caption("Recomm Town")
        self.batch = Batch()
        self.town_group = Group(order=0)
        self.people_group = Group(order=1)
        self.label_group = Group(order=2)
        self.gui_group = GuiGroup(self, order=3)
        self.move_position = Vec(0.0, 0.0)
        self.cell_range = CellRange(0, 0, 0, 0)
        self.set_view(Vec(0.0, 0.0))
        self.world = world
        self.place_index = 0
        self.human_index = 0
        self.tracked_human = None
        self.match_time = match_time

        self.human_observers: Observer[Human | None] = Observer()
        self.time_observers: Observer[int] = Observer()
        self.resize_observers: Observer[int, int] = Observer()
        self.zoom_observers: Observer[float] = Observer()

        self.__queue = queue

        self.register_event_type('on_change_place')
        self.register_event_type('on_change_human')
        self.register_event_type('on_change_page')
        self.register_event_type('on_city_zoom')

    def set_view(self, position, zoom=1.0):
        self.camera_position = position
        self.camera_zoom = zoom
        self.recreate_view()

    def recreate_view(self):
        if self._page != 'world':
            return
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
            self.label_group.visible = False
            return
        if not self.people_group.visible:
            self.people_group.visible = True
            self.label_group.visible = True
        if not is_changed:
            return
        self.zoom_observers(z)

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
        pyglet.clock.schedule_interval(self.tick_second, 1)
        pyglet.app.run()

    def tick_second(self, dt):
        self.match_time -= 1
        self.time_observers(self.match_time)
        if self.match_time <= 0:
            self.close()

    def on_key_press(self, symbol, modifiers):
        if symbol in (key.Q, SPECIAL_A):
            self.dispatch_event('on_change_place')
        if symbol in (key.W, SPECIAL_D):
            self.dispatch_event('on_change_human')
        if symbol in (key.E, SPECIAL_B):
            self.dispatch_event('on_city_zoom')
        if symbol in (key.R, SPECIAL_C):
            self.dispatch_event('on_change_page')
        if symbol == SPECIAL_UP:
            self.camera_zoom = min(10.0, self.camera_zoom * 1.05) 
            self.recreate_view()
        if symbol == SPECIAL_DOWN:
            self.camera_zoom = max(1.0, self.camera_zoom * 0.95) 
            self.recreate_view()
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

    def on_change_page(self):
        match self._page:
            case 'world':
                self.view = Mat4()
                self._page = 'graph'
                self._load_graph_image()
                pyglet.clock.schedule_interval(self._load_graph_image, 60)
            case 'graph':
                self.view = Mat4()
                self._page = 'heatmap'
                self._load_heatmap_image()
                pyglet.clock.unschedule(self._load_graph_image)
                pyglet.clock.schedule_interval(self._load_heatmap_image, 60)
            case 'heatmap':
                self._page = 'world'
                self._page_image = None
                pyglet.clock.unschedule(self._load_heatmap_image)
                self.recreate_view()

    def _load_graph_image(self, dt=0.0):
        self._load_page_image("graph.png")

    def _load_heatmap_image(self, dt=0.0):
        self._load_page_image("heatmap.png")

    def _load_page_image(self, path):
        try:
            img = image_load(path)
        except OSError:
            self._page_image = None
            return

        img.anchor_x = img.width // 2
        img.anchor_y = img.height // 2
        self._page_image = img

    def on_change_place(self):
        places = self.world.town.places
        position = places[self.place_index].position
        self._stop_tracking()
        self.set_view(position, zoom=8.0)
        self.place_index += 1
        if self.place_index >= len(places):
            self.place_index = 0

    def on_change_human(self):
        human = self.world.people[self.human_index]
        self._start_tracking(human)
        self.set_view(human.position, zoom=8.0)
        self.human_index += 1
        if self.human_index >= len(self.world.people):
            self.human_index = 0

    def on_city_zoom(self):
        self._stop_tracking()
        self.set_view(Vec(0.0, 0.0))

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
            self.human_observers(None)
            self.tracked_human = None

    def _start_tracking(self, human: Human):
        self._stop_tracking()
        self.tracked_human = human
        self.human_observers(human)
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
        self.resize_observers(width, height)
        self.recreate_view()

    def on_draw(self):
        self.clear()
        gl.glClearColor(0.79, 0.86, 0.70, 1.0)
        match self._page:
            case 'world':
                self.batch.draw()
            case 'heatmap' | 'graph':
                if self._page_image is not None:
                    self._page_image.blit(self.width // 2, self.height // 2, 0)
        gl.glFlush()

    def on_refresh(self, dt):
        try:
            event = self.__queue.get(block=False)
        except Empty:
            pass
        else:
            self.dispatch_event(event)

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
