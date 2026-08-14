from constants import EMPTY_SPACE
from display import Display
from factories.theme import Blue, Cyan, Green, Magenta, Red, White, Yellow
from three_d_renderer.constants import ASPECT_RATIO, DISTANCE_TO_SPEC
from three_d_renderer.entities.player3d import Player3D
from three_d_renderer.scenario.level3d import Level3D
from three_d_renderer.scenario.levels3d import build_level_3d_1
from utils import colored, distance_between_points, subtract_triplet, vector_length

_DEFAULT_CHAR = colored(EMPTY_SPACE, bg_color=White(0))

# TODO: this is a temporary hack
colors = [White, Cyan, Red, Blue, Green, Magenta, Yellow]
# random.shuffle(colors)


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
                vX, vY, vZ = subtract_triplet(vertex, self.player.position)

                # This is where the 3D to 2D projection magic happens
                xPos = ((vX * DISTANCE_TO_SPEC / vY) + (X_RES / 2)) if vY > 0 else 0
                yPos = (
                    (((vZ * DISTANCE_TO_SPEC / vY) + (Y_RES / 2)) / ASPECT_RATIO)
                    if vY > 0
                    else 0
                )

                if (
                    # The -1 is because of the border thickness
                    xPos < self.display.curr_x_resolution - 1
                    and yPos < self.display.curr_y_resolution - 1
                    and xPos > 1
                    and yPos > 1
                    and screen_matrix[round(yPos)][round(xPos)] == _DEFAULT_CHAR
                ):
                    vertices_to_render.append([(vX, vY, vZ), (xPos, yPos)])

            color = colors[entity.size % len(colors)]

            vertices_to_render = sorted(
                vertices_to_render,
                key=lambda e: vector_length(e[0]),
            )

            for vector, screen_position in vertices_to_render:
                xPos, yPos = screen_position
                d: float = vector_length(vector)
                max_dist = 250
                intensity: float = max(min(1 - d / max_dist, 1), 0)

                # char = "▀" if yPos % 1 > 0.5 else "▄"
                char = "█"

                defchar = colored(char, color(intensity), White(0))

                # checks if another vertex has been drawn in the specified coord and draws only the one closest to the spectator
                rounded_x_pos = round(xPos)
                rounded_y_pos = round(yPos)
                if screen_matrix[rounded_y_pos][rounded_x_pos] == _DEFAULT_CHAR:
                    screen_matrix[rounded_y_pos][rounded_x_pos] = defchar

                # just for debugging (shows vertex number)
                # screen_matrix[yPos][xPos] = str(intensity)[0]

        self.display._screen_matrix = screen_matrix
        self.display.print_curr_screen()

        # # we convert the screen matrix into a string, so we can print it
        # matrix_string = ""

        # for y in range(Y_RES):
        #     for x in range(X_RES):
        #         matrix_string += screen_matrix[y][x]
        #     if y < Y_RES - 1:
        #         matrix_string += "\n"

        # clear()

        # print(matrix_string)
