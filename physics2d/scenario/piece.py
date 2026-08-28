from abc import abstractmethod
from random import random

from factories.theme import RGB
from model.base import Point2F, Vector2F
from model.theme import Theme
from physics2d.constants import DEFAULT_GRAVITY_ACCELERATION
from physics2d.model.base import RenderInfo
from utils import add_tuple


class ScenarioPiece:
    theme: Theme
    secondary_theme: Theme | None

    name: str
    # in radians
    angle: float
    center_of_mass: Point2F

    # if > 0, it floats around randomly, like brownian motion
    floating_multi: float

    _affected_by_gravity: bool
    _own_gravity_accel: float | None
    velocity: Vector2F
    angular_velocity: Vector2F

    def __init__(
        self,
        name: str,
        center_of_mass: Point2F,
        theme: Theme = Theme(),
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: Vector2F = (0, 0),
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
    ):
        self.theme = theme
        self.name = name
        self.angle = angle

        self._affected_by_gravity = affected_by_gravity
        self.velocity = initial_velocity
        self._own_gravity_accel = own_gravity
        self.secondary_theme = secondary_theme
        self.floating_multi = floating_multi

        self.center_of_mass = center_of_mass

    def apply_gravity(self, gravity_accel: float = DEFAULT_GRAVITY_ACCELERATION) -> None:
        if not self._affected_by_gravity and not self._own_gravity_accel:
            return
        self.velocity = (
            self.velocity[0],
            self.velocity[1] - (self._own_gravity_accel or gravity_accel),
        )

    def apply_angular_momentum(self) -> None:
        pass

    def rotate(self) -> None:
        pass

    @abstractmethod
    def _get_color(cls, x: int | None = None, y: int | None = None) -> RGB:
        # Each entity should do its thing
        raise NotImplementedError(f"{cls.name or 'UnknownPiece'} must have a _get_color method")

    def _float_around(self) -> None:
        if self.floating_multi == 0:
            return

        self.velocity = add_tuple(
            self.velocity,
            (self.floating_multi * (0.5 - random()), self.floating_multi * (0.5 - random())),
        )

    @abstractmethod
    def return_render_info(cls) -> list[RenderInfo]:
        # Each entity should do its thing
        raise NotImplementedError(
            f"{cls.name or 'UnknownPiece'} must have a return_render_info method"
        )

    @abstractmethod
    def apply_movement(cls) -> None:
        # Each entity should do its thing
        raise NotImplementedError(
            f"{cls.name or 'UnknownPiece'} must have an apply_movement method"
        )
