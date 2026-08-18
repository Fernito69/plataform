from display import Display
from factories.theme import DEFAULT_CHAR
from three_d_renderer.entities.player3d import Player3D
from three_d_renderer.scenario.level_3d import Level3D
from three_d_renderer.three_d_renderer import ThreeDeeRenderer
from utils import colored, distance_between_points, has_bg_color, subtract_triplet, vector_length


class LegacyRenderer(ThreeDeeRenderer):
    def __init__(
        self,
        player: Player3D,
        display: Display,
        level: Level3D | None = None,
    ):
        ThreeDeeRenderer.__init__(self, player, display, level)

    # Legacy voxel renderer
    def visualize_scenario(self):
        X_RES = self.display.curr_x_resolution
        Y_RES = self.display.curr_y_resolution

        # we make a matrix representation of the playfield
        screen_matrix = []

        for y in range(Y_RES):
            screen_matrix.append([])
            for x in range(X_RES):
                screen_matrix[y].append(DEFAULT_CHAR)

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
                x_pos, y_pos = self._get_screen_projection(normalized_vertex)

                if (
                    # The -1 is because of the border thickness
                    x_pos < self.display.curr_x_resolution - 1
                    and y_pos < self.display.curr_y_resolution - 1
                    and x_pos > 1
                    and y_pos > 1
                    and screen_matrix[round(y_pos)][round(x_pos)] == DEFAULT_CHAR
                ):
                    vertices_to_render.append([normalized_vertex, (x_pos, y_pos)])

            color = self.colors[round(entity.size) % len(self.colors)]

            vertices_to_render = sorted(
                vertices_to_render,
                key=lambda e: vector_length(e[0]),
            )

            for vector, screen_position in vertices_to_render:
                x_pos, y_pos = screen_position
                d: float = vector_length(vector)
                intensity: float = max(min(1 - d / self.visibility_threshold, 1), 0)

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

                if screen_matrix[rounded_y_pos][rounded_x_pos] == DEFAULT_CHAR:
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
