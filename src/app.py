from dataclasses import dataclass

import pyglet
from pyglet.math import Mat4
from pyglet import gl
from pyglet.window import Window, key
from pyglet.graphics import Batch, Group


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
        w = self.width / 2
        h = self.height / 2
        self.view = self.view.translate((w, h, 0.0))
        self.view = self.view.scale((h / 1000, h / 1000, 1.0))
        self.world = world

    def run(self):
        pyglet.app.run()

    def on_key_press(self, symbol, modifiers):
        print(self.view)
        ws = 20 / self.view[0]
        if symbol == key.UP:
            self.view = self.view.translate((0.0, -ws, 0.0))
        elif symbol == key.DOWN:
            self.view = self.view.translate((0.0, +ws, 0.0))
        elif symbol == key.LEFT:
            self.view = self.view.translate((+ws, 0.0, 0.0))
        elif symbol == key.RIGHT:
            self.view = self.view.translate((-ws, 0.0, 0.0))
        else:
            return super().on_key_press(symbol, modifiers)

    def on_mouse_scroll(self, x, y, scroll_x, scroll_y):
        zoom = 1.05 if scroll_y > 0 else 0.95
        self.view = self.view.scale((zoom, zoom, 1.0))

    def on_draw(self):
        self.clear()
        gl.glClearColor(0.1, 0.5, 0.1, 1.0)
        self.batch.draw()

    def on_refresh(self, dt):
        for human in self.world.people:
            first_action = human.actions[0]
            first_action.do_it(human)
