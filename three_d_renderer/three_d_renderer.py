import random

from constants import EMPTY_SPACE
from display import Display
from factories.theme import Blue, Cyan, Green, Magenta, Red, Violet, White, Yellow
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
colors = [White, Cyan, Red, Blue, Green, Magenta, Yellow, Violet]
random.shuffle(colors)


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

    # TODO: should be level3d
    def visualize_scenario(self):
        # a = "▀"
        # b = colored(a, Red())
        # c = colored(b, bg_color=Blue())
        # self.display.debug_log(a + "|" + b + "|" + c)

        X_RES = self.display.curr_x_resolution
        Y_RES = self.display.curr_y_resolution

        # we make a matrix representation of the playfield
        screen_matrix = []

        for y in range(self.display.curr_y_resolution):
            screen_matrix.append([])
            for x in range(X_RES):
                screen_matrix[y].append(_DEFAULT_CHAR)

        # we draw the border of the screen
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
                distance_between_points(e.position, self.player.position).distance
            ),
        )
        # TODO: find a way to find what's behind the player to not render it
        for entity in self._curr_level.entities:
            # calculate movement
            entity.movement()
            entity.calc_vertexes()
            entity.apply_rotations()
            # we get vertexes from object

            # we add the vertexes to the screen matrix
            # TODO: type this shit properly
            vertices_to_render = []
            for vertex in entity.objVertexes:
                v_x, v_y, v_z = subtract_triplet(vertex, self.player.position)

                # This is where the 3D to 2D projection magic happens
                x_pos = (
                    ((v_x * self.distance_to_spec / v_y) + (X_RES / 2))
                    if v_y > 0
                    else 0
                )
                y_pos = (
                    (
                        ((v_z * self.distance_to_spec / v_y) + (Y_RES / 2))
                        / PIXEL_ASPECT_RATIO
                    )
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

            color = colors[entity.size % len(colors)]

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
                    _char
                    if isinstance(_char, str)
                    else _char[0]
                    if y_pos % 1 > 0.5
                    else _char[1]
                )

                defchar = colored(char, color=color(intensity))

                # checks if another vertex has been drawn in the specified coord and draws only the one closest to the spectator
                rounded_x_pos = round(x_pos)
                rounded_y_pos = round(y_pos)

                # curr_pixel: str = screen_matrix[rounded_y_pos][rounded_x_pos]

                if screen_matrix[rounded_y_pos][rounded_x_pos] == _DEFAULT_CHAR:
                    screen_matrix[rounded_y_pos][rounded_x_pos] = defchar
                    # screen_matrix[rounded_y_pos][rounded_x_pos] = colored(
                    #     "·", color=color(intensity)
                    # )
                    # self.display.debug_log(
                    #     "char: "
                    #     + char
                    #     + " | crr_pix: "
                    #     + curr_pixel
                    #     + " |  char not in curr_pixel:"
                    #     + str(char not in curr_pixel)
                    # )
                # we can replace it with bg_color!
                # elif char not in curr_pixel:
                # TODO: Why does this part not work??
                # TODO: implement a test for this

                elif char not in screen_matrix[rounded_y_pos][
                    rounded_x_pos
                ] and not has_bg_color(screen_matrix[rounded_y_pos][rounded_x_pos]):
                    # elif not has_bg_color(screen_matrix[rounded_y_pos][rounded_x_pos]):
                    #     and (
                    #     char not in screen_matrix[rounded_y_pos][roundesssssssssssssssssssssssssssssssssssssssd_x_pos]
                    #     if not isinstance(_char, str)
                    #     else True
                    # ):
                    # _prev_defchar = curr_pixel
                    # defchar = colored(curr_pixel, bg_color=22)

                    # if intensity > 0.7:
                    # self.display.debug_log(
                    #     defchar
                    #     + " | color:"
                    #     + str(color(intensity).r)
                    #     + " | prev dev char:"
                    #     + _prev_defchar
                    # )
                    # raise NotImplementedError("")
                    _char = colored(
                        screen_matrix[rounded_y_pos][rounded_x_pos],
                        bg_color=color(intensity),
                    )
                    self.display.debug_log(
                        "prev_pixel: "
                        + screen_matrix[rounded_y_pos][rounded_x_pos]
                        + " | defchar: "
                        + _char
                        + " | intensity:"
                        + str(color(intensity))
                    )
                    screen_matrix[rounded_y_pos][rounded_x_pos] = _char
                    # screen_matrix[rounded_y_pos][rounded_x_pos] = "A"

                # screen_matrix[rounded_y_pos][rounded_x_pos] = "C"
                # raise NotImplementedError()

                # elif (
                #     not has_bg_color(
                #         screen_matrix[rounded_y_pos][rounded_x_pos],
                #         black_is_not_condidered_bg=False,
                #     )
                #     and screen_matrix[rounded_y_pos][rounded_x_pos] != _DEFAULT_CHAR
                # ):
                # elif has_bg_color(
                #     screen_matrix[rounded_y_pos][rounded_x_pos]
                # ) and not has_color(screen_matrix[rounded_y_pos][rounded_x_pos]):

                # else:
                #     _char = colored(
                #         screen_matrix[rounded_y_pos][rounded_x_pos], color=White(1)
                #     )
                #     # self.display.debug_log(
                #     #     "prev_pixel: "
                #     #     + screen_matrix[rounded_y_pos][rounded_x_pos]
                #     #     + " | defchar: "
                #     #     + colored(
                #     #         screen_matrix[rounded_y_pos][rounded_x_pos], color=White(1)
                #     #     )
                #     # )
                #     screen_matrix[rounded_y_pos][rounded_x_pos] = colored(
                #         "A", color=White(1)
                #     )

                # just for debugging (shows vertex number)
                # screen_matrix[yPos][xPos] = str(intensity)[0]

        # screen_matrix = [
        #     [
        #         colored(
        #             char,
        #             bg_color=White(0),
        #         )
        #         for char in row
        #         if not has_bg_color(char)
        #     ]
        #     for row in screen_matrix
        # ]

        self.display.put_screen_content(screen_matrix)
        self.display.print_curr_screen()
