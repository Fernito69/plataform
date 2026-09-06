import random
from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.keyboard import MovementKeys
from model.shared import KeyboardHandler
from model.theme import RGB, Theme
from physics2d.entities.base import PhyEntity
from physics2d.scenario.pieces.circunference import CircunferencePiece
from physics2d.shapes.circunference import Circunference
from terminal import on_key_press
from utils import shuffle_list

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D

_PLAYER_RADIUS = 6
_PLAYER_THEME = Theme(color=RGB(122, 23, 255))
_PLAYER_GRAVITY = 0  # we float freely!

_MAX_MOVING_VELOCITY = 5
_ACCEL_FACTOR = 1
_DECEL_FACTOR = _ACCEL_FACTOR / 2

_MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER = 20

_THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR = 2
_THRUST_FIRE_DISTANCE_FACTOR = 1


class PlayerBlob(PhyEntity, Circunference, KeyboardHandler):
    def __init__(
        self,
        engine: "Physics2D",
        position: PointF = PointF(20, 10),
        velocity=VectorF(0, 0),
        density: float = 1,
    ):
        Circunference.__init__(self, center=position, radius=_PLAYER_RADIUS, theme=_PLAYER_THEME)
        PhyEntity.__init__(
            self,
            name="PlayerBlob",
            position=position,
            velocity=velocity,
            density=density,
            volume=self.volume,
        )
        self.engine = engine
        self.center = position
        self.position = position
        self.radius = _PLAYER_RADIUS
        self.theme = _PLAYER_THEME
        self.velocity = VectorF(0, 0)
        self.is_collideable = True
        self.name = "PlayerBlob"

    ##############
    """MOVEMENT"""
    ##############

    def do_your_thing(self) -> None:
        self.handle_keyboard_input()
        self._apply_gravity(self.engine.scenario.gravity_acceleration)
        self._apply_movement()
        self._keep_player_in_screen()
        self._handle_thrust_motor_animation()

    def _handle_thrust_motor_animation(self) -> None:
        pieces: list[CircunferencePiece] = []

        for _i in range(1, int(self.radius * 2)):
            i = _i / 2
            distance_factor = (self.radius - i) * _THRUST_FIRE_DISTANCE_FACTOR
            eye_x = self.center.x - self.velocity.x * distance_factor
            eye_y = self.center.y - self.velocity.y * distance_factor

            is_odd = _i % 2 == 1
            _randomness_multi = random.random() * 3
            _radius_factor = random.random() * 1
            # METEOR KINDA TRAIL
            # _color = (
            #     RGB(
            #         255,
            #         (i - 1) * 50,
            #         (i - 1) * 50,
            #     ).with_intensity(1)
            #     if is_odd
            #     else RGB(
            #         255,
            #         255 - (i - 1) * 30,
            #         (i - 1) * 1,
            #     ).with_intensity(1)
            # )
            # Liquid N2 trail
            _color = (
                RGB(
                    0,
                    255 - (i - 1) * 50,
                    255 - (i - 1) * 50,
                ).with_intensity(1)
                if is_odd
                else RGB(
                    0,
                    255 - (i - 1) * 30,
                    255 - (i - 1) * 1,
                ).with_intensity(1)
            )
            _affected_by_gravity = True
            _own_gravity = 0.05

            # TODO: maybe the initial_velocity should be based not ont the curr vel but rather what thrust buttons the player is hitting
            # TODO: create particle factory, extend theme for all this shit
            thrust_fire = CircunferencePiece(
                center=PointF(
                    x=eye_x
                    + shuffle_list() * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR * _randomness_multi
                    + shuffle_list() * 0.2,
                    y=eye_y
                    + shuffle_list() * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR * _randomness_multi
                    + shuffle_list() * 0.2,
                ),
                initial_velocity=VectorF(
                    x=-self.velocity.x
                    * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR
                    * _randomness_multi
                    * 0.1
                    + shuffle_list() * 0.5,
                    y=-self.velocity.y
                    * _THRUST_FIRE_SPAWN_RANDOMNESS_FACTOR
                    * _randomness_multi
                    * 0.1
                    + shuffle_list() * 0.5,
                ),
                # radius=i * math.cos((self.radius - i) / self.radius),
                radius=i * _radius_factor,
                # theme=Theme(color=RGB(140, (i - 1) * 50, (i - 1) * 100).with_intensity(1)),
                theme=Theme(color=_color),
                life_time=50,
                affected_by_gravity=_affected_by_gravity,
                own_gravity=_own_gravity,
            )
            pieces.append(thrust_fire)
            if i % 3 == 0:
                sparks = CircunferencePiece(
                    center=PointF(
                        x=eye_x + shuffle_list() * 0.2 + self.velocity.x * 3,
                        y=eye_y + shuffle_list() * 0.2 + self.velocity.y * 3,
                    ),
                    initial_velocity=VectorF(x=shuffle_list() * 7, y=random.random() * 4),
                    # radius=i * math.cos((self.radius - i) / self.radius),
                    radius=0.8,
                    # theme=Theme(color=RGB(140, (i - 1) * 50, (i - 1) * 100).with_intensity(1)),
                    theme=Theme(color=RGB(255, 255, 255, 1)),
                    life_time=50,
                    affected_by_gravity=True,
                    own_gravity=_own_gravity * 5,
                )
                pieces.append(sparks)

        pieces = sorted(pieces, key=shuffle_list)

        self.engine.scenario.bg_pieces[0:0] = pieces

        # This is if we wanted it random
        # for index in range(len(pieces)):
        #     if shuffle_list() > 0:
        #         self.engine.scenario.bg_pieces.append(pieces[index])
        #     else:
        #         self.engine.scenario.fg_pieces.append(pieces[index])

    def _move_by(self, vector: VectorF) -> None:
        # TODO: test with +=
        self.center = self.center + vector
        self.position = self.position + vector

    def _apply_gravity(self, gravity_accel: float) -> None:
        # we float freely for now
        pass

    def _apply_movement(self) -> None:
        # only solid pieces can interact with the player
        # TODO: we should filter by those that are visible on ecreen
        for piece in self.engine.scenario.solid_pieces:
            self.would_collide_with(piece, self.engine)

        self._move_by(self.velocity)

    def _keep_player_in_screen(self) -> None:
        """Adjusts the screen position in order to keep the player always visible"""
        x_res = self.engine.screen_buffer_x_res
        y_res = self.engine.screen_buffer_y_res
        player_x, player_y, _ = self.position

        if player_x < self.engine.screen_corner.x + _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER:
            self.engine.screen_corner = PointF(
                round(player_x - _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER),
                self.engine.screen_corner.y,
            )
        if player_x > self.engine.screen_corner.x + (x_res - _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER):
            self.engine.screen_corner = PointF(
                round(player_x + _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER - x_res),
                self.engine.screen_corner.y,
            )
        if player_y < self.engine.screen_corner.y + _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER:
            self.engine.screen_corner = PointF(
                self.engine.screen_corner.x,
                round(player_y - _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER),
            )
        if player_y > self.engine.screen_corner.y + y_res - _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER:
            self.engine.screen_corner = PointF(
                self.engine.screen_corner.x,
                round(player_y + _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER - y_res),
            )

    ##############
    """KEYBOARD"""
    ##############

    def handle_keyboard_input(self):
        self._move_up()
        self._move_left()
        self._move_right()
        self._move_down()

        self._decelerate_if_not_pressing()

    def _decelerate_if_not_pressing(self) -> None:
        if self.velocity.y > 0 and not self._is_pressed(MovementKeys.UP):
            self.velocity = (self.velocity + VectorF(0, -_DECEL_FACTOR)).as_vector()
        if self.velocity.y < 0 and not self._is_pressed(MovementKeys.DOWN):
            self.velocity = (self.velocity + VectorF(0, _DECEL_FACTOR)).as_vector()
        if self.velocity.x > 0 and not self._is_pressed(MovementKeys.RIGHT):
            self.velocity = (self.velocity + VectorF(-_DECEL_FACTOR, 0)).as_vector()
        if self.velocity.x < 0 and not self._is_pressed(MovementKeys.LEFT):
            self.velocity = (self.velocity + VectorF(_DECEL_FACTOR, 0)).as_vector()
        if 0 <= self.velocity.x < _DECEL_FACTOR:
            self.velocity.x = 0
        if 0 <= self.velocity.y < _DECEL_FACTOR:
            self.velocity.y = 0

    @on_key_press(MovementKeys.UP)
    def _move_up(self) -> None:
        if self.velocity.y >= _MAX_MOVING_VELOCITY:
            return

        self.velocity = (self.velocity + VectorF(0, _ACCEL_FACTOR)).as_vector()

    @on_key_press(MovementKeys.DOWN)
    def _move_down(self) -> None:
        if self.velocity.y <= -_MAX_MOVING_VELOCITY:
            return

        self.velocity = (self.velocity + VectorF(0, -_ACCEL_FACTOR)).as_vector()

    @on_key_press(MovementKeys.LEFT)
    def _move_left(self) -> None:
        if self.velocity.x <= -_MAX_MOVING_VELOCITY:
            return

        self.velocity = (self.velocity + VectorF(-_ACCEL_FACTOR, 0)).as_vector()

    @on_key_press(MovementKeys.RIGHT)
    def _move_right(self) -> None:
        if self.velocity.x >= _MAX_MOVING_VELOCITY:
            return

        self.velocity = (self.velocity + VectorF(_ACCEL_FACTOR, 0)).as_vector()
