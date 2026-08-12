import random

from constants import ENEMY_MOV_FACTOR
from entities.entity import LivingEntity
from model.enemy import EnemyType
from model.theme import Theme

_BOUNCE_FRAMES = ["_", "_", "o", "o", "O", "O"]
_MIN_BOUNCING_RANDOMNESS = 8
_MAX_BOUNCING_RANDOMNESS = 12

_STANDARD_FRAMES = ["X"]


class Enemy(LivingEntity):
    _orig_character_frames: list[str]

    def __init__(
        self,
        enemy_type: EnemyType,
        speed: float,
        movement_type: tuple[float, float],
        position: tuple[float, float],
        health: int,
        character_frames: list[str] = _STANDARD_FRAMES,
        theme: Theme | None = None,
    ):
        LivingEntity.__init__(self, health=health)
        self.enemy_type = enemy_type
        self.speed = speed
        self.position = position
        self.movement_type = movement_type
        self._character_frames = character_frames
        self._orig_character_frames = character_frames.copy()
        self.theme = theme or Theme()

    def collision(self) -> bool:
        if self.curr_level is None:
            return False

        colliding_x = self.movement_type[0] > 0 and (
            self.x_distance()[0] <= 0 or self.x_distance_neg()[0] <= 0
        )
        colliding_y = self.movement_type[1] > 0 and (
            self.y_distance()[0] <= 0 or self.y_distance_neg()[0] <= 0
        )

        if colliding_x or colliding_y:
            # Just dumbly turn around
            self.speed *= -1
            return True

        return False

    def do_your_thing(self):
        self.movement()

    def movement(self):
        if self.curr_level is None:
            return

        # Bounce enemy
        # TODO: do proper polymorphism?
        if self.enemy_type == EnemyType.DUMB_BOUNCING:
            # Go back to original characters after bouncing animation is finished
            if (
                self._character_frames == _BOUNCE_FRAMES
                and self._character_frame_index == len(_BOUNCE_FRAMES) - 1
            ):
                self._character_frames = self._orig_character_frames
                self._character_frame_index = 0

            # Has gravity and jumps!
            old_position = (self.position[0], self.position[1])
            self.apply_gravity()
            self.collision_landscape(old_position)
            self.collision_jump()

            if self.y_distance()[0] == 0:
                random_factor = (
                    0.1
                    * random.randrange(
                        _MIN_BOUNCING_RANDOMNESS, _MAX_BOUNCING_RANDOMNESS
                    )
                    if _MIN_BOUNCING_RANDOMNESS < _MAX_BOUNCING_RANDOMNESS
                    else 1
                )
                self._character_frames = _BOUNCE_FRAMES
                self._character_frame_index = 0
                self.falling_velocity = (-1) * self.movement_type[0] * random_factor
                self.move_to((0, -0.5))
                self.collision_jump()

        # Standard movement for all enemies
        self.move_to(
            (
                self.movement_type[0] * ENEMY_MOV_FACTOR * self.speed,
                self.movement_type[1] * ENEMY_MOV_FACTOR * self.speed,
            )
        )

        self.advance_character_frame()

        self.collision()
