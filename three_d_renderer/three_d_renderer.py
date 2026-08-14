import math
import random

from constants import EMPTY_SPACE
from display import Display
from factories.theme import Blue, Cyan, Green, Magenta, Red, White, Yellow
from terminal import clear
from three_d_renderer.constants import ASPECT_RATIO, DISTANCE_TO_SPEC, VISION_LIMIT
from three_d_renderer.entities.player3d import Player3D
from three_d_renderer.scenario.level3d import Level3D
from three_d_renderer.scenario.levels3d import build_level_3d_1
from utils import colored

_DEFAULT_CHAR = colored(EMPTY_SPACE, bg_color=White(0))

# TODO: this is a temporary hack
colors = [White, Cyan, Red, Blue, Green, Magenta, Yellow]
random.shuffle(colors)


# TODO: this should reuse display and set_resolution()
class ThreeDeeRenderer:
    # for now a fixed camera
    player: Player3D
    _curr_level: Level3D
    display: Display

    def __init__(
        self,
        player: Player3D,
        display: Display,
        level: Level3D | None = None,
    ):
        self.player = player
        self.display = display
        self._curr_level = level or build_level_3d_1()

    # TODO: should be level3d
    def print_scenario(self):
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

        # rendering objects
        for entity_idx, entity in enumerate(self._curr_level.entities):
            # calculate movement
            entity.movement()
            entity.calc_vertexes()
            entity.apply_rotations()
            # we get vertexes from object

            # we add the vertexes to the screen matrix
            for vertex in entity.objVertexes:
                vX = vertex[0] - self.player.position[0]
                vY = (
                    (vertex[1] - self.player.position[1])
                    if (vertex[1] - self.player.position[1]) != 0
                    else 0.001
                )
                vZ = vertex[2] - self.player.position[2]

                # This is where the 3D to 2D projection magic happens
                xPos = (
                    round((vX * DISTANCE_TO_SPEC / vY) + (X_RES / 2)) if vY > 0 else 0
                )
                yPos = (
                    round(((vZ * DISTANCE_TO_SPEC / vY) + (Y_RES / 2)) / ASPECT_RATIO)
                    if vY > 0
                    else 0
                )

                if (
                    yPos < Y_RES
                    and xPos < X_RES
                    and xPos > 0
                    and yPos > 0
                    # The -1 is because of the border thickness
                    and xPos < self.display.curr_x_resolution - 1
                    and yPos < self.display.curr_y_resolution - 1
                ):
                    # calculate distance between point and observer
                    d: int = ((vX) ** 2 + (vY) ** 2 + (vZ) ** 2) ** 0.5

                    # according to this distance, choose character
                    chars = "█▓@Øø*°,.¸"

                    char_index = max(math.floor(d / VISION_LIMIT), 0)
                    char_index = min(char_index, 9)

                    # color it
                    max_dist = 400
                    intensity: float = max(min(1 - d / max_dist, 1), 0)
                    # For now hardcode colors
                    # color = (
                    #     Red(intensity)
                    #     if entity_idx % 4 == 1
                    #     else Blue(intensity)
                    #     if entity_idx % 4 == 2
                    #     else Cyan(intensity)
                    #     if entity_idx % 4 == 3
                    #     else Green(intensity)
                    # )
                    color = colors[entity_idx % len(colors)]
                    defchar = colored(chars[char_index], color(intensity), White(0))
                    # TODO: implement debugging log in Display

                    # checks if another vertex has been drawn in the specified coord and draws only the one closest to the spectator
                    if screen_matrix[yPos][xPos] != _DEFAULT_CHAR:
                        if screen_matrix[yPos][xPos] not in chars[:char_index]:
                            screen_matrix[yPos][xPos] = defchar
                    else:
                        screen_matrix[yPos][xPos] = defchar

                    # just for debugging (shows vertex number)
                    # screen_matrix[yPos][xPos] = str(intensity)[0]

        # we convert the screen matrix into a string, so we can print it
        matrix_string = ""

        for y in range(Y_RES):
            for x in range(X_RES):
                matrix_string += screen_matrix[y][x]
            if y < Y_RES - 1:
                matrix_string += "\n"

        clear()

        print(matrix_string)
