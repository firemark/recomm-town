from math import pi, sin, cos

from pyglet.graphics import Batch
from pyglet.shapes import (
    ShapeBase,
    get_default_shader,
    GL_SRC_ALPHA,
    GL_ONE_MINUS_SRC_ALPHA,
)


class RoundedRectangle(ShapeBase):
    def __init__(
        self,
        x,
        y,
        width,
        height,
        round,
        round_verts=6,
        color=(255, 255, 255, 255),
        batch=None,
        group=None,
    ):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._rotation = 0
        self._round = round
        self._round_verts = round_verts
        self._num_verts = 5 * 6 + 4 * 3 * self._round_verts

        r, g, b, *a = color
        self._rgba = r, g, b, a[0] if a else 255

        program = get_default_shader()
        self._batch = batch or Batch()
        self._group = self.group_class(
            GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, program, group
        )

        self._create_vertex_list()
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

        r = self._round
        x1 = -self._anchor_x + r
        y1 = -self._anchor_y + r
        x2 = x1 + self._width - 2 * r
        y2 = y1 + self._height - 2 * r

        corners = [
            (x1, y1, -r, -r),
            (x2, y1, +r, -r),
            (x2, y2, +r, +r),
            (x1, y2, -r, +r),
        ]

        position = []
        for x, y, rx, ry in corners:
            xo = x
            yo = y + ry

            for i in range(1, self._round_verts + 1):
                xn = x + rx * sin(pi / 2 * i / self._round_verts)
                yn = y + ry * cos(pi / 2 * i / self._round_verts)
                # fmt: off
                position += [
                    xo, yo,
                    xn, yn,
                    x, y,
                ]
                # fmt: on
                xo, yo = xn, yn

        # fmt: off
        position += [
            x1, y1,
            x2, y1,
            x2, y2, 
            x1, y1, 
            x2, y2, 
            x1, y2,
            #
            x1    , y1,
            x1 - r, y1,
            x1 - r, y2, 
            x1    , y1, 
            x1 - r, y2, 
            x1    , y2,
            #
            x2    , y1,
            x2 + r, y1,
            x2 + r, y2, 
            x2    , y1, 
            x2 + r, y2, 
            x2    , y2,
            #
            x1, y1,
            x2, y1,
            x2, y1 - r, 
            x1, y1, 
            x2, y1 - r, 
            x1, y1 - r,
            #
            x1, y2,
            x2, y2,
            x2, y2 + r, 
            x1, y2, 
            x2, y2 + r, 
            x1, y2 + r,
        ]
        # fmt: on
        self._vertex_list.position[:] = position

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        self._update_vertices()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        self._update_vertices()
