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
    in vec4 color_r;
    in vec4 color_g;
    in vec4 color_b;
    in vec3 tex_coords;
    in vec2 position;

    out vec4 vertex_colors_r;
    out vec4 vertex_colors_g;
    out vec4 vertex_colors_b;
    out vec2 texture_coords;

    uniform WindowBlock
    {
        mat4 projection;
        mat4 view;
    } window;

    void main()
    {
        gl_Position = window.projection * window.view * vec4(position, 0.0, 1.0);

        vertex_colors_r = color_r;
        vertex_colors_g = color_g;
        vertex_colors_b = color_b;
        texture_coords = tex_coords.xy;
    }
"""

fragment_source = """#version 150 core
    in vec4 vertex_colors_r;
    in vec4 vertex_colors_g;
    in vec4 vertex_colors_b;
    in vec2 texture_coords;
    out vec4 final_colors;

    uniform sampler2D sprite_texture;

    void main()
    {
        vec4 t = texture(sprite_texture, texture_coords);
        final_colors = (
            t.r * vertex_colors_r + 
            t.g * vertex_colors_g +
            t.b * vertex_colors_b) * vec4(1.0, 1.0, 1.0, t.a);
    }
"""


def create_program():
    create_program = gl.current_context.create_program
    program = create_program((vertex_source, "vertex"), (fragment_source, "fragment"))
    return program


class Sprite:
    _vertex_list = None
    group_class = SpriteGroup

    def __init__(
        self,
        img,
        p0: Vec,
        p1: Vec,
        color_r=(255, 255, 255, 255),
        color_b=(0, 0, 0, 0),
        color_g=(0, 0, 0, 0),
        batch=None,
        group=None,
    ):
        # fmt: off
        self._v = (
            p0.x, p0.y,
            p1.x, p0.y,
            p1.x, p1.y,
            p0.x, p1.y,
        )
        # fmt: on
        self._texture = img.get_texture()
        self._program = create_program()
        self._color_r = color_r
        self._color_g = color_g
        self._color_b = color_b

        self.batch = batch
        self.group = self.group_class(
            self._texture, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA, self._program, group
        )
        self._create_vertex_list()

    def set_img(self, img):
        texture = img.get_texture()
        if texture.id is not self._texture.id:
            self.group = type(self.group)(
                texture,
                self.group.blend_src,
                self.group.blend_dest,
                self.group.program,
                self.group.parent,
            )
            if self._vertex_list is not None:
                self._vertex_list.delete()
            self._texture = texture
            self._create_vertex_list()
        elif self._vertex_list is not None:
            self._vertex_list.tex_coords[:] = texture.tex_coords
        self._texture = texture

    def set_color_r(self, color):
        self._color_r = color
        if self._vertex_list is not None:
            self._vertex_list.color_r[:] = color * 4

    def set_color_g(self, color):
        self._color_g = color
        if self._vertex_list is not None:
            self._vertex_list.color_g[:] = color * 4

    def set_color_b(self, color):
        self._color_b = color
        if self._vertex_list is not None:
            self._vertex_list.color_b[:] = color * 4

    def _create_vertex_list(self):
        self._vertex_list = self._program.vertex_list_indexed(
            4,
            GL_TRIANGLES,
            [0, 1, 2, 0, 2, 3],
            self.batch,
            self.group,
            position=("f", self._v),
            color_r=("Bn", self._color_r * 4),
            color_g=("Bn", self._color_g * 4),
            color_b=("Bn", self._color_b * 4),
            tex_coords=("f", self._texture.tex_coords),
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
        except:
            pass

    def delete(self):
        if self._vertex_list is not None:
            self._vertex_list.delete()
        self._vertex_list = None
        self._texture = None
        self._group = None
