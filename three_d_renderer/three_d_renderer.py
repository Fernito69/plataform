import random
from dataclasses import dataclass

from constants import EMPTY_SPACE
from display import Display
from factories.theme import Blue, Cyan, Green, Magenta, Orange, Red, Violet, White, Yellow
from model.shared import DistVector3D, Point2, Point3
from model.theme import RGB
from three_d_renderer.constants import (
    DEFAULT_DISTANCE_TO_SPEC,
    PIXEL_ASPECT_RATIO,
    PLAYER_3D_MOVING_SPEED_FACTOR,
)
from three_d_renderer.entities.base3d import Entity3D
from three_d_renderer.entities.player3d import Player3D
from three_d_renderer.scenario.level_3d import Level3D
from three_d_renderer.scenario.levels_3d import build_level_3d_1
from utils import colored, distance_between_points, has_bg_color, subtract_triplet, vector_length

_DEFAULT_CHAR = colored(EMPTY_SPACE, bg_color=White(0))


# TODO: Move
@dataclass
class RenderingObj:
    entity_idx: int
    entity: Entity3D
    vertex: Point3
    dist_vector: DistVector3D


@dataclass
# Represents the contribution of a line segment to filling in the pixel's content
class Contribution:
    color: RGB
    distance_from_spec: float
    """
    Usage is calculated based on how close the line passes to the center of the pixel
    e.g. at pixel (x1, y1), if the line crosses at:
    - (x1, y1) -> 0% usage, it barely touches the pixel
    - (x1 + 0.5, y1 + 0.5) -> 100% usage, the line pases exactly through the middle of the pixel
    """
    pixel_usage_ratio: float


@dataclass
class ScreenData:
    position: Point2
    contributions: list[Contribution]


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
        v_x, v_y, v_z = point3
        x_pos = ((v_x * self.fov / v_y) + (self.display.curr_x_resolution / 2)) if v_y > 0 else 0
        y_pos = (
            (((v_z * self.fov / v_y) + (self.display.curr_y_resolution / 2)) / PIXEL_ASPECT_RATIO)
            if v_y > 0
            else 0
        )
        return (x_pos, y_pos)

    def render_v2(self):
        # Order by closest to farthest
        render_list: list[RenderingObj] = sorted(
            [
                RenderingObj(
                    entity_idx=entity_idx,
                    entity=entity,
                    vertex=vertex,
                    dist_vector=distance_between_points(vertex, self.player.position),
                )
                for entity_idx, entity in [
                    (entity_idx, entity)
                    for entity_idx, entity in enumerate(self._curr_level.entities)
                ]
                for vertex in entity.objVertexes
            ],
            key=lambda r: r.dist_vector.distance,
        )

        # TODO: this doesn't go here
        screen_matrix: list[list[str]] = []

        for res in render_list:
            # With the vertex position, we project it into the screen
            pass

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
            for vertex in entity.objVertexes:
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
