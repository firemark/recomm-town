from math import fmod

from pyglet import clock
from pyglet import gl
from pyglet.sprite import (
    SpriteGroup,
    GL_SRC_ALPHA,
    GL_ONE_MINUS_SRC_ALPHA,
    GL_TRIANGLES,
)

from recomm_town.common import Vec

vertex_source = """#version 150 core
    in vec4 colors;
    in vec2 speed_coords;
    in vec2 tex_coords;
    in vec2 position;
    in float time;

    out vec4 vertex_colors;
    out vec2 texture_coords;

    uniform WindowBlock
    {
        mat4 projection;
        mat4 view;
    } window;

    void main()
    {
        gl_Position = window.projection * window.view * vec4(position, 0.0, 1.0);

        vertex_colors = colors;
        texture_coords = time * speed_coords + tex_coords;
    }
"""

fragment_source = """#version 150 core
    in vec4 vertex_colors;
    in vec2 texture_coords;
    out vec4 final_colors;

    uniform sampler2D sprite_texture;

    void main()
    {
        final_colors = texture(sprite_texture, texture_coords) * vertex_colors;
    }
"""


def create_program():
    create_program = gl.current_context.create_program
    program = create_program((vertex_source, "vertex"), (fragment_source, "fragment"))
    return program


class AnimatedLine:
    _vertex_list = None
    group_class = SpriteGroup

    def __init__(
        self,
        img,
        p0: Vec,
        p1: Vec,
        speed: Vec = Vec(0, 1),
        width: float = 1,
        dt=0.05,
        batch=None,
        group=None,
        color=(255, 255, 255, 255),
    ):
        diff = p0 - p1
        length_squared = diff.length()
        shift = diff.normalize() * width * 0.5

        # fmt: off
        self._v = (
            p0.x - shift.y, p0.y + shift.x,
            p0.x + shift.y, p0.y - shift.x,
            p1.x + shift.y, p1.y - shift.x,
            p1.x - shift.y, p1.y + shift.x,
        )
        # fmt: on
        self._texture = img.get_texture()
        self._program = create_program()
        self._repeat = Vec(1.0, length_squared / width)
        self._speed = speed
        self._color = color

        self.batch = batch
        self.group = self.group_class(
            self._texture, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, self._program, group
        )
        self.dt = dt
        self.t = 0.0
        self._create_vertex_list()
        clock.schedule_interval(self._animate, dt)

    def _create_vertex_list(self):
        rep = self._repeat
        tex_coords = (0.0, 0.0, rep.x, 0.0, rep.x, rep.y, 0.0, rep.y)
        self._vertex_list = self._program.vertex_list_indexed(
            4,
            GL_TRIANGLES,
            [0, 1, 2, 0, 2, 3],
            self.batch,
            self.group,
            position=("f", self._v),
            colors=("Bn", self._color * 4),
            speed_coords=("f", (self._speed.x, self._speed.y) * 4),
            tex_coords=("f", tex_coords),
            time=("f", (0.0,) * 4),
        )

    def draw(self):
        if self._vertex_list is None:
            return
        self.group.set_state_recursive()
        self._vertex_list.draw(GL_TRIANGLES)
        self.group.unset_state_recursive()

    def __del__(self):
        try:
            if self._vertex_list is not None:
                self._vertex_list.delete()
            clock.unschedule(self._animate)
        except:
            pass

    def _animate(self, dt):
        if self._vertex_list is None:
            return  # Deleted in event handler.
        self.t = fmod(self.t + dt, 1.0)
        self._vertex_list.time[:] = (self.t,) * 4

    def delete(self):
        clock.unschedule(self._animate)
        if self._vertex_list is not None:
            self._vertex_list.delete()
        self._vertex_list = None
        self._texture = None
        self._group = None
