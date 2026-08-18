import random

from display import Display
from factories.theme import Blue, Cyan, Green, Magenta, Orange, Red, Violet, White, Yellow
from model.base import Point2, Point3
from three_d_renderer.constants import (
    DEFAULT_DISTANCE_TO_SPEC,
    DEFAULT_VISIBILITY_THRESHOLD,
    PIXEL_ASPECT_RATIO,
    PLAYER_3D_MOVING_SPEED_FACTOR,
)
from three_d_renderer.entities.player3d import Player3D
from three_d_renderer.scenario.level_3d import Level3D
from three_d_renderer.scenario.levels_3d import build_level_3d_1

# TODO: this is a temporary hack
colors = [White, Cyan, Red, Blue, Green, Magenta, Yellow, Violet, Orange]
random.shuffle(colors)


# TODO: this should reuse display and set_resolution()
class ThreeDeeRenderer:
    # for now a fixed camera
    player: Player3D
    _curr_level: Level3D
    display: Display

    # physics params
    curr_player_speed = PLAYER_3D_MOVING_SPEED_FACTOR
    visibility_threshold: int
    fov: float

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
        self.fov = DEFAULT_DISTANCE_TO_SPEC
        self.visibility_threshold = DEFAULT_VISIBILITY_THRESHOLD
        self.curr_player_speed = PLAYER_3D_MOVING_SPEED_FACTOR
        # TODO: this is a temporary hack
        self.colors = colors

    # This is where the 3D to 2D projection magic happens
    def _get_screen_projection(self, point3: Point3) -> Point2:
        x, y, z = point3
        x_pos = ((x * self.fov / y) + (self.display.curr_x_resolution / 2)) if y > 0 else 0
        y_pos = (
            (((z * self.fov / y) + (self.display.curr_y_resolution / 2)) / PIXEL_ASPECT_RATIO)
            if y > 0
            else 0
        )
        return (x_pos, y_pos)
