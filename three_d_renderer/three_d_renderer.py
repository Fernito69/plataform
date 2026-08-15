import random

from constants import EMPTY_SPACE
from display import Display
from factories.theme import (
    Blue,
    Cyan,
    Green,
    Magenta,
    Orange,
    Red,
    Violet,
    White,
    Yellow,
)
from three_d_renderer.constants import (
    DEFAULT_DISTANCE_TO_SPEC,
    DEFAULT_VISIBILITY_LIMIT,
    PIXEL_ASPECT_RATIO,
    PLAYER_3D_MOVING_SPEED_FACTOR,
)
from three_d_renderer.entities.player3d import Player3D
from three_d_renderer.scenario.level_3d import Level3D
from three_d_renderer.scenario.levels_3d import build_level_3d_1
from utils import (
    colored,
    distance_between_points,
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
    current_speed = PLAYER_3D_MOVING_SPEED_FACTOR
    curr_distance_fog: int
    distance_to_spec: float

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
        self.distance_to_spec = DEFAULT_DISTANCE_TO_SPEC
        self.curr_distance_fog = DEFAULT_VISIBILITY_LIMIT
        self.current_speed = PLAYER_3D_MOVING_SPEED_FACTOR
        # TODO: this is a temporary hack
        self.colors = colors

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
                v_x, v_y, v_z = subtract_triplet(vertex, self.player.position)

                # This is where the 3D to 2D projection magic happens
                x_pos = ((v_x * self.distance_to_spec / v_y) + (X_RES / 2)) if v_y > 0 else 0
                y_pos = (
                    (((v_z * self.distance_to_spec / v_y) + (Y_RES / 2)) / PIXEL_ASPECT_RATIO)
                    if v_y > 0
                    else 0
                )

                if (
                    # The -1 is because of the border thickness
                    x_pos < self.display.curr_x_resolution - 1
                    and y_pos < self.display.curr_y_resolution - 1
                    and x_pos > 1
                    and y_pos > 1
                    and screen_matrix[round(y_pos)][round(x_pos)] == _DEFAULT_CHAR
                ):
                    vertices_to_render.append([(v_x, v_y, v_z), (x_pos, y_pos)])

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
