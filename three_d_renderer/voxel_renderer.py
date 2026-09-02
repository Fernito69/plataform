from typing import TYPE_CHECKING

from factories.theme import DEFAULT_CHAR, DoubleLines
from model.base import PointF
from model.theme import LOWER_PIXEL_CHAR, UPPER_PIXEL_CHAR
from three_d_renderer.three_d_renderer import ThreeDeeRenderer
from utils import colored, distance_between_points, has_bg_color

if TYPE_CHECKING:
    from game import Game


class VoxelRenderer(ThreeDeeRenderer):
    def __init__(self, game: "Game"):
        ThreeDeeRenderer.__init__(self, game)
        self.draw_screen_border()

    def draw_screen_border(self):
        X_RES = self.display.curr_x_resolution
        Y_RES = self.display.curr_y_resolution

        self._screen_buffer[0][0] = DoubleLines.UL
        self._screen_buffer[Y_RES - 1][X_RES - 1] = DoubleLines.LR
        self._screen_buffer[0][X_RES - 1] = DoubleLines.UR
        self._screen_buffer[Y_RES - 1][0] = DoubleLines.LL

        for y in range(1, Y_RES - 1):
            self._screen_buffer[y][0] = DoubleLines.V
            self._screen_buffer[y][X_RES - 1] = DoubleLines.V

        for x in range(1, X_RES - 1):
            self._screen_buffer[0][x] = DoubleLines.H
            self._screen_buffer[Y_RES - 1][x] = DoubleLines.H

    def main_loop(self) -> None:
        self.draw_screen_border()
        self.game.player3d.handle_keyboard_input()
        self.calculate_scenario()
        self.visualize_scenario()

    def calculate_scenario(self):
        for entity in self.game.player3d.curr_level.entities:
            entity.calc_legacy_voxels()
            entity.movement()

    def visualize_scenario(self, border_thickness: int = 1):
        player = self.game.player3d
        if not player.curr_level:
            return

        X_RES = self.display.curr_x_resolution
        Y_RES = self.display.curr_y_resolution

        # we make a matrix representation of the playfield
        self.reset_screen_buffer(keep_border=True)

        # rendering objects, we sort them first by distance
        player.curr_level.entities = sorted(
            player.curr_level.entities,
            key=lambda e: (
                # TODO: this distance_to_edge is sus af, make it right
                distance_between_points(
                    e.position, player.position, e.get_diameter()
                ).distance_to_edge
                or 0
            ),
        )

        for entity in player.curr_level.entities:
            vertices_to_render: list[tuple[PointF, PointF]] = []

            # TODO: render distance is not working well, fix
            for vertex in entity.vertices:
                vertex_seen_from_player: PointF = self._normalize_vertex_to_entity(vertex, player)
                screen_pos = self._get_screen_projection(vertex_seen_from_player)

                if (
                    screen_pos.x < X_RES - border_thickness
                    and screen_pos.y < Y_RES - border_thickness
                    and screen_pos.x > border_thickness
                    and screen_pos.y > border_thickness
                    and self._screen_buffer[round(screen_pos.y)][round(screen_pos.x)]
                    == DEFAULT_CHAR
                ):
                    vertices_to_render.append(
                        (vertex_seen_from_player, PointF(screen_pos.x, screen_pos.y))
                    )

            color = self.colors[round(entity.size) % len(self.colors)]

            vertices_to_render = sorted(
                vertices_to_render,
                key=lambda e: abs(e[0]),
            )

            for vector, screen_position in vertices_to_render:
                x_pos, y_pos, _ = screen_position
                d: float = abs(vector)
                intensity: float = max(min(1 - d / self.visibility_threshold, 1), 0)

                char: str = UPPER_PIXEL_CHAR if y_pos % 1 > 0.5 else LOWER_PIXEL_CHAR
                colored_char = colored(char, color=color(intensity))

                # checks if another vertex has been drawn in the specified coord and draws only the one closest to the spectator
                rounded_x_pos = round(x_pos)
                rounded_y_pos = round(y_pos)

                if self._screen_buffer[rounded_y_pos][rounded_x_pos] == DEFAULT_CHAR:
                    self._screen_buffer[rounded_y_pos][rounded_x_pos] = colored_char
                # TODO: implement a test for this, not sure if works as intended
                elif char not in self._screen_buffer[rounded_y_pos][
                    rounded_x_pos
                ] and not has_bg_color(self._screen_buffer[rounded_y_pos][rounded_x_pos]):
                    _char = colored(
                        self._screen_buffer[rounded_y_pos][rounded_x_pos],
                        bg_color=color(intensity),
                    )
                    self._screen_buffer[rounded_y_pos][rounded_x_pos] = _char

        self.display.put_screen_content(self._screen_buffer)
        self.display.print_curr_screen(player)
