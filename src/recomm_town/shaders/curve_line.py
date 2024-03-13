from math import radians, sin, cos

from pyglet.graphics import Batch
from pyglet.shapes import (
    ShapeBase,
    get_default_shader,
    GL_SRC_ALPHA,
    GL_ONE_MINUS_SRC_ALPHA,
)

from recomm_town.common import Vec


class CurveLine(ShapeBase):
    def __init__(
        self,
        x,
        y,
        thickness,
        round,
        width,
        height,
        arc_verts=6,
        color=(255, 255, 255, 255),
        rotation=0,
        anchor_position=(0, 0),
        batch=None,
        group=None,
    ):
        self._x = x
        self._y = y
        self._thickness = thickness
        self._round = round
        self._width = width
        self._height = height
        self._arc_verts = arc_verts
        self._num_verts = 6 * self._arc_verts + 12

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        program = get_default_shader()
        self._batch = batch or Batch()
        self._group = self.group_class(
            GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, program, group
        )

        self._create_vertex_list()
        self._update_vertices()
        self.rotation = rotation
        self.anchor_position = anchor_position

    def _create_vertex_list(self):
        self._vertex_list = self._group.program.vertex_list(
            self._num_verts,
            self._draw_mode,
            self._batch,
            self._group,
            colors=("Bn", self._rgba * self._num_verts),
            translation=("f", (self._x, self._y) * self._num_verts),
        )

    def _update_vertices(self):
        if not self._visible:
            self._vertex_list.position[:] = (0, 0) * self._num_verts
            return

        h = self._height
        w = self._width
        ri = self._round
        ro = ri + self._thickness
        dr = self._thickness
        fa = radians(90)
        sh = +1 if h > 0 else -1
        sw = +1 if w > 0 else -1
        x = -self._anchor_x + (ro - self._thickness // 2) * sw
        y = -self._anchor_y + (ro - self._thickness // 2) * sh

        vis = Vec(x, y - ri * sh)
        vos = Vec(x, y - ro * sh)

        position = []
        for i in range(1, self._arc_verts + 1):
            a = fa * i / self._arc_verts
            vie = Vec(x - ri * sin(a) * sw, y - ri * cos(a) * sh)
            voe = Vec(x - ro * sin(a) * sw, y - ro * cos(a) * sh)

            # fmt: off
            position += [
                vis.x, vis.y,
                vos.x, vos.y,
                voe.x, voe.y,
                vis.x, vis.y,
                vie.x, vie.y,
                voe.x, voe.y,
            ]
            # fmt: on

            vis = vie
            vos = voe

        a = Vec(x, y - ro * sh)
        b = a + Vec(w, dr * sh)
        # fmt: off
        position += [
            a.x, a.y,
            b.x, a.y,
            b.x, b.y,
            a.x, a.y,
            a.x, b.y,
            b.x, b.y,
        ]
        # fmt: on

        a = Vec(x - ro * sw, y)
        b = a + Vec(dr * sw, h)
        # fmt: off
        position += [
            a.x, a.y,
            b.x, a.y,
            b.x, b.y,
            a.x, a.y,
            a.x, b.y,
            b.x, b.y,
        ]
        # fmt: on
        self._vertex_list.position[:] = position