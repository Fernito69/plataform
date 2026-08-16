import math
import random

from constants import EMPTY_SPACE
from display import Display
from factories.theme import Blue, Cyan, Green, Magenta, Orange, Red, Violet, White, Yellow
from model.base import Point2, Point3
from three_d_renderer.constants import (
    DEFAULT_DISTANCE_TO_SPEC,
    PIXEL_ASPECT_RATIO,
    PLAYER_3D_MOVING_SPEED_FACTOR,
)
from three_d_renderer.entities.player3d import Player3D
from three_d_renderer.model.base import (
    PixelContribution,
    RenderingObj,
    ScreenData,
    SubpixelContribution,
    Vertex3,
)
from three_d_renderer.scenario.level_3d import Level3D
from three_d_renderer.scenario.levels_3d import build_level_3d_1
from utils import (
    colored,
    distance_between_points,
    distance_from_line_to_point,
    get_line_equations,
    has_bg_color,
    subtract_triplet,
    vector_length,
)

_DEFAULT_CHAR = colored(EMPTY_SPACE, bg_color=White(0))

# TODO: this is a temporary hack
colors = [White, Cyan, Red, Blue, Green, Magenta, Yellow, Violet, Orange]
random.shuffle(colors)

# TODO: make color oscillate with time!


# TODO: this should reuse display and set_resolution()
class ThreeDeeRenderer:
    # for now a fixed camera
    player: Player3D
    _curr_level: Level3D
    display: Display

    # physics params
    curr_player_speed = PLAYER_3D_MOVING_SPEED_FACTOR
    curr_distance_fog: int
    fov: float

    # TODO: this is a temporary hack
    colors: list

    def __init__(
        self,
        player: Player3D,
        display: Display,
        level: Level3D | None = None,
    ):
        self.player = player
        self.display = display
        self._curr_level = level or build_level_3d_1()
        self.fov = DEFAULT_DISTANCE_TO_SPEC
        self.curr_distance_fog = 170
        # self.curr_distance_fog = DEFAULT_VISIBILITY_LIMIT
        self.curr_player_speed = PLAYER_3D_MOVING_SPEED_FACTOR
        # TODO: this is a temporary hack
        self.colors = colors

    # This is where the 3D to 2D projection magic happens
    def _project_onto_screen(self, point3: Point3) -> Point2:
        x, y, z = point3
        x_pos = ((x * self.fov / y) + (self.display.curr_x_resolution / 2)) if y > 0 else 0
        y_pos = (
            (((z * self.fov / y) + (self.display.curr_y_resolution / 2)) / PIXEL_ASPECT_RATIO)
            if y > 0
            else 0
        )
        return (x_pos, y_pos)

    def render_v2(self):
        # Order vertices by closest to farthest
        render_list: list[RenderingObj] = sorted(
            [
                RenderingObj(
                    entity_idx=entity_idx,
                    entity=entity,
                    vertex=Vertex3(point=vertex, index=vertex_index),
                    dist_vector=distance_between_points(vertex, self.player.position),
                )
                for entity_idx, entity in [
                    (entity_idx, entity)
                    for entity_idx, entity in enumerate(self._curr_level.entities)
                ]
                for vertex_index, vertex in enumerate(entity.vertices)
            ],
            key=lambda r: r.dist_vector.distance,
        )

        screen_data: list[list[ScreenData | None]] = []
        # Init screen_data
        for y in range(self.display.curr_y_resolution):
            screen_data.append([])
            for _ in range(self.display.curr_x_resolution):
                screen_data[y].append(None)

        for res in render_list:
            # 1) Take vertices and trace lines
            # 2) Figure out pixels the line goes through
            # 3) Figure out pixel_usage_ratio

            connections = [c for c in res.entity.vertex_connections if c[0] == res.vertex.index]

            # Calc lines
            for _, connecting_vertex_index in connections:
                curr_vertex = self._project_onto_screen(res.vertex.point)
                connecting_vertex = self._project_onto_screen(
                    res.entity.vertices[connecting_vertex_index]
                )

                # TODO: Wait, this doesn't necessarily mean the line it generates is not visible! This needs to be fixed
                if not self.display.is_in_screen(curr_vertex) and not self.display.is_in_screen(
                    connecting_vertex
                ):
                    continue

                # Trace line
                eq = get_line_equations(curr_vertex, connecting_vertex)

                # we gather every individual contribution of the entity line to the pixel.
                contributions: list[PixelContribution] = []

                # Check the affected pixels:
                x1, y1 = curr_vertex
                x2, y2 = connecting_vertex
                for x in range(math.floor(min(x1, x2)), math.ceil(max(x1, x2))):
                    for y in range(math.floor(min(y1, y2)), math.ceil(max(y1, y2))):
                        calculated_y = eq.get_y(x)
                        calculated_x = eq.get_x(calculated_y)
                        # TODO: Round or floor?
                        if round(calculated_y) == y and round(calculated_x) == x:
                            # Calculate pixel_usage_ratio per half
                            # we use the half's middle point

                            # Upper pixel limits -> (x,y) (x+1, y + .5)
                            middle_upper = (x + 0.5, y + 0.25)
                            # Upper pixel limits:
                            # (x,y+.5) (x+1, y + 1)
                            middle_lower = (x + 0.5, y + 0.75)

                            # What's the max distance? from the middle to the corner -> sqrt(.25^2+.5^2) -> 0.559
                            # We take that as 0% contribution, and 0 as 100%
                            def get_contribution(x: float, y: float):
                                return max(
                                    1
                                    - distance_from_line_to_point(
                                        (curr_vertex, connecting_vertex),
                                        (x, y),
                                    )
                                    / 0.559,
                                    0,
                                )

                            upper_contribution = get_contribution(*middle_upper)
                            lower_contribution = get_contribution(*middle_lower)

                            if upper_contribution <= 0 and lower_contribution <= 0:
                                continue

                            upper_subpixel = SubpixelContribution(
                                color=res.entity.theme.color,
                                distance_from_spec=res.dist_vector.distance,
                                pixel_usage_ratio=upper_contribution,
                            )

                            lower_subpixel = SubpixelContribution(
                                color=res.entity.theme.color,
                                distance_from_spec=res.dist_vector.distance,
                                pixel_usage_ratio=lower_contribution,
                            )

                            contributions.append(
                                PixelContribution(
                                    upper_subpixel=upper_subpixel, lower_subpixel=lower_subpixel
                                )
                            )

    def visualize_scenario(self):
        X_RES = self.display.curr_x_resolution
        Y_RES = self.display.curr_y_resolution

        # we make a matrix representation of the playfield
        screen_matrix = []

        for y in range(self.display.curr_y_resolution):
            screen_matrix.append([])
            for x in range(X_RES):
                screen_matrix[y].append(_DEFAULT_CHAR)

        # we draw the border of the screen
        # TODO: this shit we should do only once!
        screen_matrix[0][0] = "╔"
        screen_matrix[Y_RES - 1][X_RES - 1] = "╝"
        screen_matrix[0][X_RES - 1] = "╗"
        screen_matrix[Y_RES - 1][0] = "╚"

        for y in range(1, Y_RES - 1):
            screen_matrix[y][0] = "║"
            screen_matrix[y][X_RES - 1] = "║"

        for x in range(1, X_RES - 1):
            screen_matrix[0][x] = "═"
            screen_matrix[Y_RES - 1][x] = "═"

        # rendering objects, we sort them first by distance
        self._curr_level.entities = sorted(
            self._curr_level.entities,
            key=lambda e: (
                # distance_between_points(e.position, self.player.position).distance
                # TODO: if I add the size it does it wrong, figure out what the shit
                # TODO: figured out the shit! it requires a factor now because size is not normalized between entities
                # TODO: this shold be distance to vertex!!!!????
                distance_between_points(
                    e.position, self.player.position, e.get_diameter()
                ).distance_to_edge
                or 0
            ),
        )

        # TODO: find a way to find what's behind the player to not render it
        # TODO: refactor, beri messy right now
        for entity in self._curr_level.entities:
            # calculate movement
            entity.movement()
            entity.calc_vertexes()
            entity.apply_rotations()
            # we get vertexes from object

            # we add the vertexes to the screen matrix
            # TODO: type this shit properly
            vertices_to_render = []
            # TODO: Hmmm here is where we should filter out by distance to fix the error with the big dodeca?
            for vertex in entity.vertices:
                normalized_vertex = subtract_triplet(vertex, self.player.position)
                x_pos, y_pos = self._project_onto_screen(normalized_vertex)

                if (
                    # The -1 is because of the border thickness
                    x_pos < self.display.curr_x_resolution - 1
                    and y_pos < self.display.curr_y_resolution - 1
                    and x_pos > 1
                    and y_pos > 1
                    and screen_matrix[round(y_pos)][round(x_pos)] == _DEFAULT_CHAR
                ):
                    vertices_to_render.append([normalized_vertex, (x_pos, y_pos)])

            color = self.colors[entity.size % len(self.colors)]

            vertices_to_render = sorted(
                vertices_to_render,
                key=lambda e: vector_length(e[0]),
            )

            for vector, screen_position in vertices_to_render:
                x_pos, y_pos = screen_position
                d: float = vector_length(vector)
                intensity: float = max(min(1 - d / self.curr_distance_fog, 1), 0)

                # TODO: make these symbols consts
                _char: str | list[str] = self.display.curr_3d_char_mode
                # TODO: generalize to any length of array
                char: str = (
                    _char if isinstance(_char, str) else _char[0] if y_pos % 1 > 0.5 else _char[1]
                )

                defchar = colored(char, color=color(intensity))

                # checks if another vertex has been drawn in the specified coord and draws only the one closest to the spectator
                rounded_x_pos = round(x_pos)
                rounded_y_pos = round(y_pos)

                # curr_pixel: str = screen_matrix[rounded_y_pos][rounded_x_pos]

                if screen_matrix[rounded_y_pos][rounded_x_pos] == _DEFAULT_CHAR:
                    screen_matrix[rounded_y_pos][rounded_x_pos] = defchar
                # TODO: implement a test for this, not sure if works as intended
                elif char not in screen_matrix[rounded_y_pos][rounded_x_pos] and not has_bg_color(
                    screen_matrix[rounded_y_pos][rounded_x_pos]
                ):
                    _char = colored(
                        screen_matrix[rounded_y_pos][rounded_x_pos],
                        bg_color=color(intensity),
                    )
                    screen_matrix[rounded_y_pos][rounded_x_pos] = _char

        self.display.put_screen_content(screen_matrix)
        self.display.print_curr_screen(self.player)
