from abc import abstractmethod

from model.base import VectorF
from model.theme import RGB
from physics2d.entities.base import PhysicsEntity
from physics2d.entities.model.shared import ParticleGenerator
from physics2d.shape.model.shared import TransitionType


class Particle:
    initial_color: RGB
    ending_color: RGB | None
    ending_color_fade_type: TransitionType

    # numbers of "game ticks" that they will survive (None means they don't die out)
    life_time: int | None
    _original_life_time: int | None

    size_change_type: TransitionType

    _particle_generator: ParticleGenerator | None

    def __init__(
        self,
        initial_color: RGB,
        ending_color: RGB | None = None,
        initial_velocity: VectorF = VectorF(0, 0),
        life_time: int | None = None,
        size_change_type: TransitionType = TransitionType.NONE,
        ending_color_fade_type: TransitionType = TransitionType.LINEAR_DECREASE,
        floating_multi: float = 0,
        particle_generator: ParticleGenerator | None = None,
    ):
        self.life_time = life_time
        self._original_life_time = life_time
        self.initial_color = initial_color
        self.ending_color = ending_color
        self.ending_color_fade_type = ending_color_fade_type
        self.size_change_type = size_change_type
        self.initial_velocity = initial_velocity
        self.floating_multi = floating_multi
        self._particle_generator = particle_generator

    def do_your_thing(self) -> None:
        from physics2d.entities.equipment.projectile import Projectile

        self._handle_life_time()

        # TODO: fix this, should apply for any shape/entity
        if self._particle_generator and isinstance(self, PhysicsEntity):
            self._particle_generator(self._engine, self)
        if isinstance(self, Projectile) and self._trail_generator:
            self._trail_generator(self._engine, self, self.target)

    @abstractmethod
    def _handle_life_time(cls) -> None: ...
