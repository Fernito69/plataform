from abc import abstractmethod
from typing import TYPE_CHECKING

from constants import ALMOST_ZERO
from model.base import PointF, VectorF
from model.theme import RGB, Theme
from physics2d.constants import DEFAULT_GRAVITY_ACCELERATION
from physics2d.model.shared import RenderInfo
from utils import random_offset

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class Shape:
    _engine: "Physics2D"

    name: str
    theme: Theme
    secondary_theme: Theme | None
    # TODO: do right and make it mandatory!

    # in radians
    angle: float
    center_of_mass: PointF
    _affected_by_gravity: bool
    _own_gravity_accel: float | None
    velocity: VectorF
    _last_known_direction: VectorF
    angular_velocity: float
    # if > 0, it floats around randomly, like brownian motion
    floating_multi: float

    density: float
    volume: float
    weight: float

    is_collideable: bool

    affected_by_friction: bool

    """renders behind the player even if in the foreground layer"""
    render_behind_player: bool

    def __init__(
        self,
        center_of_mass: PointF,
        name: str,
        density: float,
        volume: float,
        engine: "Physics2D",
        theme: Theme = Theme(),
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: VectorF = VectorF(0, 0),
        initial_angular_velocity: float = 0,
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
        is_collideable: bool = False,
        affected_by_friction: bool = False,
        render_behind_player: bool = False,
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
        self.is_collideable = is_collideable
        self.affected_by_friction = affected_by_friction
        self.render_behind_player = render_behind_player
        self._engine = engine

    def set_last_known_direction(self) -> None:
        # HACK, let's see if helps
        if abs(self.velocity.x) < ALMOST_ZERO and abs(self.velocity.y) < ALMOST_ZERO:
            return
        self._last_known_direction = self.velocity.unit_vector()

    def get_last_known_direction(self, scale: float = 1) -> VectorF:
        raw = self._last_known_direction or self.velocity.unit_vector()
        return (scale * raw).as_vector() if scale != 1 else raw

    @abstractmethod
    def do_your_thing(self) -> None:
        ...
        # Each entity should do its thing
        # raise NotImplementedError(f"{self.name or 'Shape'} must have a do_your_thing method")

    @abstractmethod
    def would_collide_with(self, shape: "Shape") -> bool:
        """Determines whether the current shape would collide with a particular shape, given their location"""

        # Each shape should do its thing
        raise NotImplementedError(f"Shape must have a would_collide_with method")

    @abstractmethod
    def get_render_info(cls) -> list[RenderInfo]:
        # Each shape should do its thing
        raise NotImplementedError(f"Shape must have a get_render_info method")

    def _apply_gravity(self, gravity_accel: float = DEFAULT_GRAVITY_ACCELERATION) -> None:
        if not self._affected_by_gravity and not self._own_gravity_accel:
            return
        self.velocity = VectorF(
            self.velocity.x,
            self.velocity.y - (self._own_gravity_accel or gravity_accel),
        )

    @abstractmethod
    def _apply_collisions(self) -> None:
        # Each shape should do its thing
        raise NotImplementedError(f"Shape must have an _apply_collisions method")

    @abstractmethod
    def _update_center_of_mass(cls) -> None:
        # Each entity should do its thing
        raise NotImplementedError(f"{cls.name or 'Shape'} must have a _calc_center_of_mass method")

    @abstractmethod
    def _rotate(cls) -> None:
        # Each entity should do its thing
        raise NotImplementedError(f"{cls.name or 'Shape'} must have a _rotate method")

    @abstractmethod
    def _get_color(cls, x: int | None = None, y: int | None = None) -> RGB:
        # Each entity should do its thing
        raise NotImplementedError(f"{cls.name or 'Shape'} must have a _get_color method")

    def _float_around(self) -> None:
        if self.floating_multi == 0:
            return

        self.velocity = (
            self.velocity
            + VectorF(self.floating_multi * random_offset(), self.floating_multi * random_offset())
        ).as_vector()

    @abstractmethod
    def _apply_movement(cls) -> None:
        # Each entity should do its thing
        raise NotImplementedError(f"{cls.name or 'Shape'} must have an _apply_movement method")

    @abstractmethod
    def _move_by(self, vector: VectorF) -> None:
        # Each entity should do its thing
        raise NotImplementedError(f"{self.name or 'Shape'} must have a _move_by method")

    @abstractmethod
    def _apply_angular_momentum(self, momentum: VectorF) -> None:
        # TODO: implement
        ...
