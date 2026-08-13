import math

from terminal import clear
from three_d_renderer.constants import (
    ASPECT_RATIO,
    DISTANCE_TO_SPEC,
    VISION_LIMIT,
    X_RESOLUTION_3D,
    Y_RESOLUTION_3D,
)
from three_d_renderer.entities.player3d import Player3D
from three_d_renderer.scenario.level3d import Level3D
from three_d_renderer.scenario.levels3d import build_level_3d_1


# TODO: this should reuse display and set_resolution()
class ThreeDeeRenderer:
    # for now a fixed camera
    player: Player3D
    _curr_level: Level3D

    def __init__(
        self,
        player: Player3D,
        level: Level3D | None = None,
    ):
        self.player = player
        self._curr_level = level or build_level_3d_1()

    # TODO: should be level3d
    def print_scenario(self):

        # we make a matrix representation of the playfield
        screen_matrix = []

        for y in range(Y_RESOLUTION_3D):
            screen_matrix.append([])
            for x in range(X_RESOLUTION_3D):
                screen_matrix[y].append(" ")

        # we draw the border of the screen
        screen_matrix[0][0] = "╔"
        screen_matrix[Y_RESOLUTION_3D - 1][X_RESOLUTION_3D - 1] = "╝"
        screen_matrix[0][X_RESOLUTION_3D - 1] = "╗"
        screen_matrix[Y_RESOLUTION_3D - 1][0] = "╚"

        for y in range(1, Y_RESOLUTION_3D - 1):
            screen_matrix[y][0] = "║"
            screen_matrix[y][X_RESOLUTION_3D - 1] = "║"

        for x in range(1, X_RESOLUTION_3D - 1):
            screen_matrix[0][x] = "═"
            screen_matrix[Y_RESOLUTION_3D - 1][x] = "═"

        # rendering objects
        for entity in self._curr_level.entities:
            # calculate movement
            entity.movement()
            entity.calc_vertexes()
            entity.apply_rotations()

            # we get vertexes from object

            # we add the vertexes to the screen matrix
            for vertex in entity.objVertexes:
                vX = vertex[0]
                vY = vertex[1] if vertex[1] != 0 else 0.001
                vZ = vertex[2]

                xPos = (
                    int(round(vX * DISTANCE_TO_SPEC / vY) + round(X_RESOLUTION_3D / 2))
                    if vY > 0
                    else 0
                )
                yPos = (
                    int(
                        round((vZ * DISTANCE_TO_SPEC / vY) + round(Y_RESOLUTION_3D / 2))
                        / ASPECT_RATIO
                    )
                    if vY > 0
                    else 0
                )

                if (
                    yPos < Y_RESOLUTION_3D
                    and xPos < X_RESOLUTION_3D
                    and xPos > 0
                    and yPos > 0
                ):
                    # calculate distance between point and observer
                    d = (vX**2 + vY**2 + vZ**2) ** 0.5

                    # according to this distance, choose character
                    chars = "█▓@Øø*°,.¸"

                    # if its x,y coordinates are negative, just don't draw the character
                    index = (
                        int(math.floor(d / VISION_LIMIT))
                        if int(math.floor(d / VISION_LIMIT)) >= 0
                        else 0
                    )
                    index = index if index <= 9 else 9

                    defchar = chars[index]

                    # checks if another vertex has been drawn in the specified coord and draws only the one closest to the spectator
                    if screen_matrix[yPos][xPos] != " ":
                        if (
                            screen_matrix[yPos][xPos] not in chars[:index]
                            and screen_matrix[yPos][xPos] not in "║═╚╝╔╗"
                        ):
                            screen_matrix[yPos][xPos] = defchar
                    else:
                        screen_matrix[yPos][xPos] = defchar

                    # just for debugging (shows vertex number)
                    # screen_matrix[yPos][xPos] = vertex[3]

        # we convert the screen matrix into a string, so we can print it
        matrix_string = ""

        for y in range(Y_RESOLUTION_3D):
            for x in range(X_RESOLUTION_3D):
                matrix_string += screen_matrix[y][x]
            if y < Y_RESOLUTION_3D - 1:
                matrix_string += "\n"

        clear()

        print(matrix_string)
