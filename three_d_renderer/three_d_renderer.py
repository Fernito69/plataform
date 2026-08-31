import random
from typing import TYPE_CHECKING

from factories.theme import (
    DEFAULT_CHAR,
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
from model.base import Point2F, Point3F
from model.shared import Engine
from three_d_renderer.constants import (
    DEFAULT_DISTANCE_TO_SPEC,
    DEFAULT_VISIBILITY_THRESHOLD,
    PIXEL_ASPECT_RATIO,
    PLAYER_3D_MOVING_SPEED_FACTOR,
)
from three_d_renderer.entities.base3d import Entity3D
from utils import rotate_point, subtract_triplet

if TYPE_CHECKING:
    from game import Game

# TODO: this is a temporary hack
colors = [White, Cyan, Red, Blue, Green, Magenta, Yellow, Violet, Orange]
random.shuffle(colors)


class ThreeDeeRenderer(Engine):
    _screen_buffer: list[list[str]] = []

    # physics params
    curr_player_speed = PLAYER_3D_MOVING_SPEED_FACTOR
    visibility_threshold: int
    fov: float

    # TODO: this is a temporary hack
    colors: list

    def __init__(self, game: "Game"):
        self.game = game
        self.display = self.game.display
        self.fov = DEFAULT_DISTANCE_TO_SPEC
        self.visibility_threshold = DEFAULT_VISIBILITY_THRESHOLD
        # TODO: this doesn't go here
        self.curr_player_speed = PLAYER_3D_MOVING_SPEED_FACTOR
        # TODO: this is a temporary hack
        self.colors = colors
        self.reset_screen_buffer()

    def reset_screen_buffer(self, keep_border: bool = False, border_thickness: int = 1):
        X_RES = self.display.curr_x_resolution
        Y_RES = self.display.curr_y_resolution

        if keep_border:
            for y in range(border_thickness, Y_RES - border_thickness):
                for x in range(border_thickness, X_RES - border_thickness):
                    self._screen_buffer[y][x] = DEFAULT_CHAR
        else:
            self._screen_buffer: list[list[str]] = []
            for y in range(Y_RES):
                self._screen_buffer.append([])
                for _ in range(X_RES):
                    self._screen_buffer[y].append(DEFAULT_CHAR)

    # This is where the 3D to 2D projection magic happens
    def _get_screen_projection(self, point3: Point3F, player: Entity3D | None = None) -> Point2F:
        x, y, z = self._normalize_vertex_to_entity(point3, player) if player else point3

        x_pos = ((x * self.fov / y) + (self.display.curr_x_resolution / 2)) if y > 0 else 0
        y_pos = (
            (((z * self.fov / y) + (self.display.curr_y_resolution / 2)) / PIXEL_ASPECT_RATIO)
            if y > 0
            else 0
        )
        return (x_pos, y_pos)

    def _normalize_vertex_to_entity(self, vertex1: Point3F, entity: Entity3D) -> Point3F:
        """takes an absolutely-positioned vertex and transforms it according to an entities' position and angle"""
        # Normalize by angle: for now only x-axis, since we have only one degree of freedom for rotation
        rotated_vertex = (
            *rotate_point(
                (vertex1[0], vertex1[1]),
                (entity.position[0], entity.position[1]),
                -entity._angle[0],
            ),
            vertex1[2],
        )
        # Normalize by position
        return subtract_triplet(rotated_vertex, entity.position)
