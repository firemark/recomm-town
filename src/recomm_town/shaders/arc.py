from math import radians, sin, cos

from pyglet.graphics import Batch
from pyglet.shapes import (
    ShapeBase,
    get_default_shader,
    GL_SRC_ALPHA,
    GL_ONE_MINUS_SRC_ALPHA,
)

from recomm_town.common import Vec


class Arc(ShapeBase):
    def __init__(
        self,
        x,
        y,
        inner_radius,
        outer_radius,
        start_angle: float = 0.0,
        angle: float = 90.0,
        arc_verts=32,
        color=(255, 255, 255, 255),
        batch=None,
        group=None,
    ):
        self._x = x
        self._y = y
        self._inner_radius = inner_radius
        self._outer_radius = outer_radius
        self._start_angle = start_angle
        self._angle = angle
        self._arc_verts = arc_verts
        self._num_verts = 6 * self._arc_verts

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        program = get_default_shader()
        self._batch = batch or Batch()
        self._group = self.group_class(
            GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, program, group
        )

        self._create_vertex_list()
        self._update_vertices()

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, value):
        self._angle = value
        self._update_vertices()

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

        ri = self._inner_radius
        ro = self._outer_radius
        sa = radians(self._start_angle)
        fa = radians(self._angle)
        x = 0.0
        y = 0.0

        vis = Vec(x + ri * sin(sa), y + ri * cos(sa))
        vos = Vec(x + ro * sin(sa), y + ro * cos(sa))

        position = []
        for i in range(1, self._arc_verts + 1):
            a = sa + fa * i / self._arc_verts
            vie = Vec(x + ri * sin(a), y + ri * cos(a))
            voe = Vec(x + ro * sin(a), y + ro * cos(a))

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
        self._vertex_list.position[:] = position