from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.entities.enemy import Enemy
from physics2d.model.shared import RenderInfo
from physics2d.shape.base import Shape
from physics2d.shape.factories.explosion import enemy_explosion
from physics2d.shape.line import Line
from three_d_renderer.entities.base3d import Entity3D
from utils import project_3d_into_2d

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class ThreeDeeEnemy(Enemy):
    _engine: "Physics2D"

    polyhedron: Entity3D
    _line_thickness: float
    visibility_threshold: float

    def __init__(
        self,
        engine: "Physics2D",
        polyhedron: Entity3D,
        health: float | None,
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
        visibility_threshold: float = 0.007,
        line_thickness: float = 1,
        color_cycling_factor: float = 57,
    ):
        self._engine = engine
        self.polyhedron = polyhedron
        self.visibility_threshold = visibility_threshold
        self.theme = theme
        self._line_thickness = line_thickness
        self._color_cycling_factor = color_cycling_factor

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
            engine=engine,
            color_cycling_factor=color_cycling_factor,
        )
        self.health = health
        self._initial_health = health
        self._initial_theme = Theme(color=theme.color)
        self.name = name
        self.extra_shapes = extra_shapes

    def do_your_thing(self) -> None:
        self.polyhedron.calc_legacy_voxels()
        self.polyhedron.movement()
        self._cycle_color()
        super().do_your_thing()

    #################################################################
    """ RENDERING """
    #################################################################

    def get_render_info(self) -> list[RenderInfo]:
        return (
            self._get_render_info_v1()
            if self._engine.low_quality_mode
            else self._get_render_info_like_line_renderer()
        )

    def _get_render_info_v1(self) -> list[RenderInfo]:
        vertices_to_render: list[tuple[PointF, PointF]] = []
        entity = self.polyhedron

        # TODO: render distance is not working well, fix
        for vertex in entity.vertices:
            vertex_seen_from_player = vertex
            screen_pos = project_3d_into_2d(vertex_seen_from_player, self._engine.get_resolution())

            if not screen_pos:
                continue

            X_RES, Y_RES = self._engine.get_resolution()

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

    def _get_render_info_like_line_renderer(self) -> list[RenderInfo]:
        vertices_in_3d = [
            (
                v,
                abs(v),
            )
            for v in self.polyhedron.vertices
        ]

        lines_to_render: list[RenderInfo] = []

        sorted_connections = sorted(
            self.polyhedron.vertex_connections,
            key=lambda c: vertices_in_3d[c[0]][1] + vertices_in_3d[c[1]][1],
        )

        # TODO: fix it to use this
        # sorted_connections = self.polyhedron.get_sorted_vertex_connections()

        for num_a, num_b in sorted_connections:
            first_vertex, first_distance = vertices_in_3d[num_a]
            second_vertex, second_distance = vertices_in_3d[num_b]
            projected_point_1 = project_3d_into_2d(first_vertex, self._engine.get_resolution())
            projected_point_2 = project_3d_into_2d(second_vertex, self._engine.get_resolution())

            if not projected_point_1 or not projected_point_2:
                continue

            X_RES, Y_RES = self._engine.get_resolution()
            x_min, y_min, _ = self._engine.screen_corner
            x_max = x_min + X_RES
            y_max = y_min + Y_RES

            # TODO: the logic should not that dumb, we need at least one of them to be in the screen
            if (
                projected_point_1.x < x_max
                and projected_point_1.y < y_max
                and projected_point_1.x > x_min
                and projected_point_1.y > y_min
            ) or (
                projected_point_2.x < x_max
                and projected_point_2.y < y_max
                and projected_point_2.x > x_min
                and projected_point_2.y > y_min
            ):
                # TODO: make self.visibility_threshold not a float
                _factor = 1 / self.visibility_threshold
                intensity_1: float = max(min(1 - first_distance / _factor, 1), 0)
                intensity_2: float = max(min(1 - second_distance / _factor, 1), 0)
                color = self.theme.color or RGB()
                line = Line(
                    points=(projected_point_1, projected_point_2),
                    engine=self._engine,
                    theme=Theme(
                        color=color.with_intensity(intensity_1),
                    ),
                    secondary_theme=Theme(
                        color=color.with_intensity(intensity_2),
                    ),
                    thickness=self._line_thickness,
                )
                lines_to_render.extend(line.get_render_info())

        return lines_to_render

    def die(self, _death_explosion_size: int | None = None) -> None:
        enemy_explosion(self._engine, self, _death_explosion_size or self.radius * 2)
        self._engine.scenario.three_dee_enemies = [
            e for e in self._engine.scenario.three_dee_enemies if e is not self
        ]
