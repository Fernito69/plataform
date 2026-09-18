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
from model.base import PointF, VectorF
from model.shared import Engine
from three_d_renderer.constants import (
    DEFAULT_DISTANCE_TO_SPEC,
    DEFAULT_VISIBILITY_THRESHOLD,
    PLAYER_3D_MOVING_SPEED_FACTOR,
)
from three_d_renderer.entities.base3d import Entity3D
from utils import normalize_vertex_according_to_another, project_3d_into_2d

if TYPE_CHECKING:
    from display import Display
    from game import Game

# TODO: this is a temporary hack
colors = [White, Cyan, Red, Blue, Green, Magenta, Yellow, Violet, Orange]
random.shuffle(colors)


class ThreeDeeRenderer(Engine):
    _display: "Display"
    _screen_buffer: list[list[str]] = []

    # physics params
    curr_player_speed = PLAYER_3D_MOVING_SPEED_FACTOR
    visibility_threshold: int
    fov: float

    # TODO: this is a temporary hack
    colors: list

    def __init__(self, game: "Game"):
        self.game = game
        self._display = self.game.display
        self.fov = DEFAULT_DISTANCE_TO_SPEC
        self.visibility_threshold = DEFAULT_VISIBILITY_THRESHOLD
        # TODO: this doesn't go here
        self.curr_player_speed = PLAYER_3D_MOVING_SPEED_FACTOR
        # TODO: this is a temporary hack
        self.colors = colors
        self.reset_screen_buffer()

    def reset_screen_buffer(self, keep_border: bool = False, border_thickness: int = 1):
        X_RES, Y_RES = self._display.get_resolution()

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

    def _get_screen_projection(
        self,
        point3: PointF,
        player: Entity3D | None = None,
    ) -> PointF | None:
        return project_3d_into_2d(
            point3=point3,
            spec_position=player.position if player else PointF(0, 0, 0),
            spec_angle=player.angle if player else VectorF(0, 0, 0),
            curr_resolution=self._display.get_resolution(),
            fov=self.fov,
        )

    def _normalize_vertex_to_entity(self, vertex1: PointF, entity: Entity3D) -> PointF:
        return normalize_vertex_according_to_another(vertex1, entity.position, entity.angle)
