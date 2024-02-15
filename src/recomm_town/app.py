import pyglet
from pyglet.gl import gl
from pyglet.math import Mat4
from pyglet.window import Window, key
from pyglet.graphics import Batch, Group

from recomm_town.common import Vec


class App(Window):
    batch: Batch
    town_group: Group
    people_group: Group

    _zoom: float

    def __init__(self, world):
        super().__init__(width=800, height=600)
        self.batch = Batch()
        self.town_group = Group(order=0)
        self.people_group = Group(order=1)
        self.move_position = Vec(0.0, 0.0)
        self.set_view(Vec(0.0, 0.0))
        self.world = world
        self.place_index = 0

    def set_view(self, position, zoom=1.0):
        self.camera_position = position
        self.camera_zoom = zoom
        self.recreate_view()

    def recreate_view(self):
        w = self.width / 2
        h = self.height / 2
        z = self.camera_zoom * h / 4000.0
        p = self.camera_position * -z + Vec(w, h)
        view = Mat4()
        view = view.translate((p.x, p.y, 0.0))
        view = view.scale((z, z, 1.0))
        self.view = view

    def run(self):
        pyglet.app.run()

    def on_key_press(self, symbol, modifiers):
        if symbol == key.Q:
            places = self.world.town.places
            position = places[self.place_index].position
            self.set_view(position, zoom=8.0)
            self.place_index += 1
            if self.place_index >= len(places):
                self.place_index = 0
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
            self.recreate_view()
        elif symbol == key.DOWN:
            self.move_position -= Vec(0.0, -20.0)
            self.recreate_view()
        elif symbol == key.LEFT:
            self.move_position -= Vec(-20.0, 0.0)
            self.recreate_view()
        elif symbol == key.RIGHT:
            self.move_position -= Vec(+20.0, 0.0)
            self.recreate_view()
        else:
            return super().on_key_press(symbol, modifiers)

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
