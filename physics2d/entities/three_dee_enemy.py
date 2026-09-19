from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.entities.enemy import Enemy
from physics2d.model.shared import RenderInfo
from physics2d.shape.base import Shape
from three_d_renderer.entities.base3d import Entity3D
from utils import project_3d_into_2d

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class ThreeDeeEnemy(Enemy):
    # TOOD: this should apply for all entites actually, and stop drilling it via do_your_thing
    engine: "Physics2D"

    polyhedron: Entity3D
    visibility_threshold: float

    def __init__(
        self,
        engine: "Physics2D",
        polyhedron: Entity3D,
        health: float,
        density: float = 1,
        name: str = "3DEnemy",
        position: PointF = PointF(0, 0),
        theme: Theme = Theme(),
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        initial_angular_velocity: float = 0,
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
        extra_shapes: list[Shape] = [],
        visibility_threshold: float = 0.01,
    ):
        self.engine = engine
        self.polyhedron = polyhedron
        self.visibility_threshold = visibility_threshold
        self.theme = theme

        super().__init__(
            size=polyhedron.get_diameter(),
            health=health,
            density=density,
            name=name,
            position=position,
            theme=theme,
            angle=angle,
            affected_by_gravity=affected_by_gravity,
            initial_velocity=initial_velocity,
            initial_angular_velocity=initial_angular_velocity,
            own_gravity=own_gravity,
            secondary_theme=secondary_theme,
            floating_multi=floating_multi,
            extra_shapes=extra_shapes,
        )
        self.health = health
        self._initial_health = health
        self._initial_theme = Theme(color=theme.color)
        self.name = name
        self.extra_shapes = extra_shapes

    def do_your_thing(self, engine: "Physics2D") -> None:
        self.polyhedron.calc_legacy_voxels()
        self.polyhedron.movement()

        super().do_your_thing(engine)

    #################################################################
    """ RENDERING """

    #################################################################
    def get_render_info(self) -> list[RenderInfo]:
        vertices_to_render: list[tuple[PointF, PointF]] = []
        entity = self.polyhedron

        # TODO: render distance is not working well, fix
        for vertex in entity.vertices:
            # vertex_seen_from_player: PointF = normalize_vertex_according_to_another(
            #     vertex, PointF(0, 0, 0), VectorF(0, 0, 0)
            # )
            vertex_seen_from_player = vertex
            screen_pos = project_3d_into_2d(
                vertex_seen_from_player, self.engine.get_resolution(), pixel_aspect_ratio=1
            )

            if not screen_pos:
                continue

            X_RES, Y_RES = self.engine.get_resolution()

            if (
                screen_pos.x < X_RES
                and screen_pos.y < Y_RES
                and screen_pos.x > 0
                and screen_pos.y > 0
            ):
                vertices_to_render.append((vertex_seen_from_player, screen_pos))

        color = self.theme.color or RGB()

        vertices_to_render = sorted(
            vertices_to_render,
            key=lambda e: abs(e[0]),
        )

        _screen_buffer: dict[int, dict[int, RenderInfo]] = {}

        for vector, screen_position in vertices_to_render:
            x_pos, y_pos, _ = screen_position
            rounded_x_pos = round(x_pos)
            rounded_y_pos = round(y_pos)

            d: float = abs(vector)
            intensity: float = max(min(1 - d / 160, 1), 0)
            # intensity: float = vertex.z

            _buffer_y = _screen_buffer.get(rounded_y_pos)

            if _buffer_y is None:
                _screen_buffer[rounded_y_pos] = {}

            if _buffer_y is not None:
                if not _buffer_y.get(rounded_x_pos):
                    info = RenderInfo(
                        point=PointF(rounded_x_pos, rounded_y_pos),
                        distance_to_pixel_center=0,  # ???
                        color=color.with_intensity(intensity),
                    )
                    _screen_buffer[rounded_y_pos][rounded_x_pos] = info
                else:
                    _screen_buffer[rounded_y_pos][rounded_x_pos].color = _screen_buffer[
                        rounded_y_pos
                    ][rounded_x_pos].color.mix_with(color.with_intensity(intensity))

        return [x for y in _screen_buffer.values() for x in y.values()]

        #     char: str = UPPER_PIXEL_CHAR if y_pos % 1 > 0.5 else LOWER_PIXEL_CHAR
        #     colored_char = colored(char, color=color.with_intensity(intensity))

        #     # checks if another vertex has been drawn in the specified coord and draws only the one closest to the spectator
        #     rounded_x_pos = round(x_pos)
        #     rounded_y_pos = round(y_pos)

        #     if self._screen_buffer[rounded_y_pos][rounded_x_pos] == DEFAULT_CHAR:
        #         self._screen_buffer[rounded_y_pos][rounded_x_pos] = colored_char
        #     # TODO: implement a test for this, not sure if works as intended
        #     elif char not in self._screen_buffer[rounded_y_pos][rounded_x_pos] and not has_bg_color(
        #         self._screen_buffer[rounded_y_pos][rounded_x_pos]
        #     ):
        #         _char = colored(
        #             self._screen_buffer[rounded_y_pos][rounded_x_pos],
        #             bg_color=color.with_intensity(intensity),
        #         )
        #         self._screen_buffer[rounded_y_pos][rounded_x_pos] = _char

        # for y in len(self._screen_buffer):
        #     for x in len(self._screen_buffer[y]):
        #         render_info.append(RenderInfo(point=PointF(x, y), distance_to_pixel_center=0, color=))
