from abc import abstractmethod
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.constants import DEFAULT_GRAVITY_ACCELERATION
from physics2d.model.shared import RenderInfo
from utils import shuffle_list

if TYPE_CHECKING:
    from physics2d.scenario.scenario import Scenario


class Shape:
    name: str
    theme: Theme
    secondary_theme: Theme | None

    # in radians
    angle: float
    center_of_mass: PointF
    _affected_by_gravity: bool
    _own_gravity_accel: float | None
    velocity: VectorF
    angular_velocity: float
    # if > 0, it floats around randomly, like brownian motion
    floating_multi: float

    density: float
    volume: float
    weight: float

    def __init__(
        self,
        center_of_mass: PointF,
        name: str,
        density: float,
        volume: float,
        theme: Theme = Theme(),
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        initial_angular_velocity: float = 0,
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
    ):
        self.theme = theme
        self.secondary_theme = secondary_theme
        self.name = name
        self.angle = angle
        self._affected_by_gravity = affected_by_gravity
        self.velocity = initial_velocity
        self._own_gravity_accel = own_gravity
        self.floating_multi = floating_multi
        self.angular_velocity = initial_angular_velocity
        self.center_of_mass = center_of_mass
        self.density = density
        self.volume = volume
        self.weight = density * volume

    def _apply_gravity(self, gravity_accel: float = DEFAULT_GRAVITY_ACCELERATION) -> None:
        if not self._affected_by_gravity and not self._own_gravity_accel:
            return
        self.velocity = VectorF(
            self.velocity.x,
            self.velocity.y - (self._own_gravity_accel or gravity_accel),
        )

    @abstractmethod
    def get_render_info(cls) -> list[RenderInfo]:
        # Each shape should do its thing
        raise NotImplementedError(f"Shape must have a get_render_info method")

    @abstractmethod
    def would_collide_with(self, shape: "Shape") -> bool:
        """Determines wheter the current shape would collide with a particular shape, given their location"""

        # Each shape should do its thing
        raise NotImplementedError(f"Shape must have a would_collide method")

    @abstractmethod
    def apply_angular_momentum(self, momentum: VectorF) -> None:
        # TODO: implement
        pass

    @abstractmethod
    def update_center_of_mass(cls) -> None:
        # Each entity should do its thing
        raise NotImplementedError(
            f"{cls.name or 'UnknownPiece'} must have a calc_center_of_mass method"
        )

    @abstractmethod
    def rotate(cls) -> None:
        # Each entity should do its thing
        raise NotImplementedError(f"{cls.name or 'UnknownPiece'} must have a rotate method")

    @abstractmethod
    def _get_color(cls, x: int | None = None, y: int | None = None) -> RGB:
        # Each entity should do its thing
        raise NotImplementedError(f"{cls.name or 'UnknownPiece'} must have a _get_color method")

    def _float_around(self) -> None:
        if self.floating_multi == 0:
            return

        self.velocity = (
            self.velocity
            + VectorF(self.floating_multi * shuffle_list(), self.floating_multi * shuffle_list())
        ).as_vector()

    @abstractmethod
    def _apply_movement(cls, scenario: "Scenario") -> None:
        # Each entity should do its thing
        raise NotImplementedError(
            f"{cls.name or 'UnknownPiece'} must have an apply_movement method"
        )
