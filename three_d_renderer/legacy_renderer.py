from display import Display
from factories.theme import DEFAULT_CHAR
from model.theme import DoubleLines
from three_d_renderer.entities.player3d import Player3D
from three_d_renderer.three_d_renderer import ThreeDeeRenderer
from utils import colored, distance_between_points, has_bg_color, subtract_triplet, vector_length


class LegacyRenderer(ThreeDeeRenderer):
    def __init__(
        self,
        player: Player3D,
        display: Display,
    ):
        ThreeDeeRenderer.__init__(self, player, display)
        self.draw_screen_border()

    def draw_screen_border(self):
        X_RES = self.display.curr_x_resolution
        Y_RES = self.display.curr_y_resolution

        self._screen_matrix_buffer[0][0] = DoubleLines.UL
        self._screen_matrix_buffer[Y_RES - 1][X_RES - 1] = DoubleLines.LR
        self._screen_matrix_buffer[0][X_RES - 1] = DoubleLines.UR
        self._screen_matrix_buffer[Y_RES - 1][0] = DoubleLines.LL

        for y in range(1, Y_RES - 1):
            self._screen_matrix_buffer[y][0] = DoubleLines.V
            self._screen_matrix_buffer[y][X_RES - 1] = DoubleLines.V

        for x in range(1, X_RES - 1):
            self._screen_matrix_buffer[0][x] = DoubleLines.H
            self._screen_matrix_buffer[Y_RES - 1][x] = DoubleLines.H

    # Legacy voxel renderer
    def visualize_scenario(self):
        X_RES = self.display.curr_x_resolution
        Y_RES = self.display.curr_y_resolution

        # we make a matrix representation of the playfield
        self.reset_screen_buffer(keep_border=True)

        # rendering objects, we sort them first by distance
        self._curr_level.entities = sorted(
            self._curr_level.entities,
            key=lambda e: (
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
            entity.calc_legacy_voxels()
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
                    x_pos < X_RES - 1
                    and y_pos < Y_RES - 1
                    and x_pos > 1
                    and y_pos > 1
                    and self._screen_matrix_buffer[round(y_pos)][round(x_pos)] == DEFAULT_CHAR
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

                if self._screen_matrix_buffer[rounded_y_pos][rounded_x_pos] == DEFAULT_CHAR:
                    self._screen_matrix_buffer[rounded_y_pos][rounded_x_pos] = defchar
                # TODO: implement a test for this, not sure if works as intended
                elif char not in self._screen_matrix_buffer[rounded_y_pos][
                    rounded_x_pos
                ] and not has_bg_color(self._screen_matrix_buffer[rounded_y_pos][rounded_x_pos]):
                    _char = colored(
                        self._screen_matrix_buffer[rounded_y_pos][rounded_x_pos],
                        bg_color=color(intensity),
                    )
                    self._screen_matrix_buffer[rounded_y_pos][rounded_x_pos] = _char

        self.display.put_screen_content(self._screen_matrix_buffer)
        self.display.print_curr_screen(self.player)
