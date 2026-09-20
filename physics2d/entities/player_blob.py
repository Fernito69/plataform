from typing import TYPE_CHECKING

from model.base import PointF, VectorF
from model.keyboard import ActionKeys, CheatKeys, MovementKeys
from model.theme import RGB, Theme
from physics2d.entities.base import PhysicsEntity
from physics2d.entities.equipment.thruster import Thruster
from physics2d.entities.equipment.thrusters.basic_thruster import BasicThruster
from physics2d.entities.equipment.thrusters.meteor_thruster import MeteorThruster
from physics2d.entities.equipment.thrusters.plasma_ball_thruster import PlasmaBallThruster
from physics2d.entities.equipment.thrusters.soapy_thruster import SoapyThruster
from physics2d.entities.equipment.thrusters.sonic_thruster import SonicThruster
from physics2d.entities.equipment.weapon import Weapon
from physics2d.entities.equipment.weapons.bfg import BFG
from physics2d.entities.equipment.weapons.death_ray import DeathRay
from physics2d.entities.equipment.weapons.homing_missile_launcher import HomingMissileLauncher
from physics2d.entities.equipment.weapons.lightning_gun import LightningGun
from physics2d.entities.equipment.weapons.machine_gun import HeavyMachineGun, MachineGun
from physics2d.entities.equipment.weapons.rocket_launcher import HeavyRocketLauncher, RocketLauncher
from physics2d.entities.equipment.weapons.shotgun import Shotgun
from physics2d.entities.equipment.weapons.zapper import Zapper
from physics2d.shape.model.shared import TransitionType
from physics2d.shape.particle.circular_particle import CircularParticle
from player import Player
from system import consume_mouse_scroll, on_key_press, on_mouse_press

_INITIAL_HEALTH = 100

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D
    from physics2d.scenario.scenario import Scenario

_PLAYER_RADIUS = 4

_PLAYER_THEME = Theme(color=RGB(122, 23, 255))
_CROSSHAIR_PARTICLE_NAME = "CrosshairParticle"

_MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER = 20


class PlayerBlob(PhysicsEntity, Player):
    _thrusters: list[Thruster]
    _curr_thruster_index: int
    _last_known_direction: VectorF

    _weapons: list[Weapon]
    _curr_weapon_index: int

    def __init__(
        self,
        engine: "Physics2D",
        position: PointF = PointF(0, 0),
        velocity=VectorF(0, 0),
        density: float = 1,
        player_number: int = 1,
        lives: int = 3,
        points: int = 0,
        health: float = _INITIAL_HEALTH,
    ):
        PhysicsEntity.__init__(
            self,
            name="PlayerBlob",
            engine=engine,
            position=position,
            initial_velocity=velocity,
            density=density,
            size=_PLAYER_RADIUS,
            theme=_PLAYER_THEME,
        )
        Player.__init__(
            self,
            player_number=player_number,
            lives=lives,
            points=points,
            health=health,
        )
        self._engine = engine
        self.center = position
        self.position = position
        self.radius = _PLAYER_RADIUS
        self.theme = _PLAYER_THEME
        self.velocity = velocity
        self.is_collideable = True
        self._last_known_direction = velocity
        self.name = "PlayerBlob"

    ##############
    """MOVEMENT"""
    ##############

    def do_your_thing(self) -> None:
        self.get_curr_thruster().handle_particles()
        self.get_curr_weapon().do_your_thing()

        self._handle_mouse_input()
        self.handle_keyboard_input()
        self._apply_gravity(self._engine.scenario.gravity_acceleration)
        self._apply_movement()
        self._keep_player_in_screen()

    def _move_by(self, vector: VectorF) -> None:
        self.center += vector
        self.position += vector

    def _apply_gravity(self, gravity_accel: float) -> None:
        # we float freely for now
        pass

    def _apply_movement(self) -> None:
        # only solid pieces can interact with the player
        # TODO: we should filter by those that are visible on ecreen
        for piece in self._engine.scenario.solid_shapes + self._engine.scenario.enemies:
            self.would_collide_with(piece)

        self._move_by(self.velocity)

    def _keep_player_in_screen(self) -> None:
        """Adjusts the screen position in order to keep the player always visible"""
        x_res, y_res = self._engine.get_resolution()
        player_x, player_y, _ = self.position

        if player_x < self._engine.screen_corner.x + _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER:
            self._engine.screen_corner = PointF(
                round(player_x - _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER),
                self._engine.screen_corner.y,
            )
        if player_x > self._engine.screen_corner.x + (
            x_res - _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER
        ):
            self._engine.screen_corner = PointF(
                round(player_x + _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER - x_res),
                self._engine.screen_corner.y,
            )
        if player_y < self._engine.screen_corner.y + _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER:
            self._engine.screen_corner = PointF(
                self._engine.screen_corner.x,
                round(player_y - _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER),
            )
        if player_y > self._engine.screen_corner.y + y_res - _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER:
            self._engine.screen_corner = PointF(
                self._engine.screen_corner.x,
                round(player_y + _MIN_PLAYER_DISTANCE_TO_SCREEN_BORDER - y_res),
            )

    def get_curr_thruster(self) -> Thruster:
        return self._thrusters[self._curr_thruster_index]

    def get_curr_weapon(self) -> Weapon:
        return self._weapons[self._curr_weapon_index]

    def get_fire_direction(self) -> VectorF:
        _screen_pos = self._engine.screen_corner

        return (
            (
                self._engine.scenario.crosshair.position
                - VectorF(
                    self.position.x - _screen_pos.x,
                    self.position.y - _screen_pos.y,
                )
            )
            .as_vector()
            .unit_vector()
        )

    def get_weapon_position(self) -> PointF:
        return self.center + self.radius * self.get_fire_direction()

    def _get_max_speed(self) -> float:
        return self.get_curr_thruster().max_speed

    def _get_accel(self) -> float:
        return self.get_curr_thruster().accel

    def _get_decel(self) -> float:
        return self.get_curr_thruster().decel

    def init_player(self) -> None:
        if not self._scenario:
            return

        self._thrusters = [
            BasicThruster(self._engine),
            SoapyThruster(self._engine),
            MeteorThruster(self._engine),
            SonicThruster(self._engine),
            PlasmaBallThruster(self._engine),
        ]
        self._curr_thruster_index = 0
        self._weapons = [
            MachineGun(self._engine),
            Shotgun(self._engine),
            LightningGun(self._engine),
            HeavyMachineGun(self._engine),
            RocketLauncher(self._engine),
            HomingMissileLauncher(self._engine),
            HeavyRocketLauncher(self._engine),
            Zapper(self._engine),
            DeathRay(self._engine),
            BFG(self._engine),
        ]
        self._curr_weapon_index = 0
        self.theme = self.get_curr_thruster().player_theme

    def set_scenario(self, scenario: "Scenario") -> None:
        self._scenario = scenario
        self.init_player()

    def _cycle_weapon(self, direction: int) -> None:
        self._curr_weapon_index = (self._curr_weapon_index + direction) % len(self._weapons)

    def _decelerate_if_not_pressing(self) -> None:
        _decel_amount = self._get_decel()
        _max_speed = self._get_max_speed()
        if (
            self.velocity.y > 0 and not self._is_pressed(MovementKeys.UP)
        ) or self.velocity.y > _max_speed:
            self.velocity = (
                self.velocity + VectorF(0, -min(_decel_amount, self.velocity.y))
            ).as_vector()
        if (
            self.velocity.y < 0 and not self._is_pressed(MovementKeys.DOWN)
        ) or self.velocity.y < -_max_speed:
            self.velocity = (
                self.velocity + VectorF(0, max(_decel_amount, self.velocity.y))
            ).as_vector()
        if (
            self.velocity.x > 0 and not self._is_pressed(MovementKeys.RIGHT)
        ) or self.velocity.x > _max_speed:
            self.velocity = (
                self.velocity + VectorF(-min(_decel_amount, self.velocity.x), 0)
            ).as_vector()
        if (
            self.velocity.x < 0 and not self._is_pressed(MovementKeys.LEFT)
        ) or self.velocity.x < -_max_speed:
            self.velocity = (
                self.velocity + VectorF(max(_decel_amount, self.velocity.x), 0)
            ).as_vector()

    ###############
    """  INPUT  """
    ###############

    def handle_keyboard_input(self):
        self._switch_thruster()
        self._move_up()
        self._move_left()
        self._move_right()
        self._move_down()
        self._next_weapon()
        self._previous_weapon()
        self._decelerate_if_not_pressing()

        # cheats
        self._kill_all_monsters()

    def _handle_mouse_input(self) -> None:
        self._shoot()
        self._add_indicator_on_target_point()

        steps = consume_mouse_scroll()

        if steps:
            # Up → next weapon; down → previous weapon.
            self._cycle_weapon(steps)

    @on_mouse_press()
    def _shoot(self) -> None:
        self.get_curr_weapon().fire()

    @on_mouse_press(act_once_per_press=True)
    def _add_indicator_on_target_point(self) -> None:

        # if any(p for p in self.engine.scenario.bg_pieces if p.name == _CROSSHAIR_PARTICLE_NAME):
        #     return
        _light = CircularParticle(
            name=_CROSSHAIR_PARTICLE_NAME,
            origin=self._engine.scenario.crosshair.center + self._engine.screen_corner,
            size=0.1,
            final_radius=8,
            life_time=10,
            initial_color=RGB(255, 100, 100),
            ending_color=RGB(60, 0, 0),
            size_change_type=TransitionType.LINEAR_INCREASE,
            engine=self._engine,
        )
        # self.engine.scenario.bg_pieces = [
        #     p for p in self.engine.scenario.bg_pieces if p.name != _CROSSHAIR_PARTICLE_NAME
        # ]
        self._engine.scenario.bg_shapes[0:0] = [_light]

    @on_key_press(ActionKeys.NEXT_WEAPON, act_once_per_press=True)
    def _next_weapon(self) -> None:
        self._cycle_weapon(1)

    @on_key_press(ActionKeys.PREVIOUS_WEAPON, act_once_per_press=True)
    def _previous_weapon(self) -> None:
        self._cycle_weapon(-1)

    @on_key_press(ActionKeys.SWITCH_THRUSTER, act_once_per_press=True)
    def _switch_thruster(self) -> None:
        self._curr_thruster_index = (
            self._curr_thruster_index + 1
            if len(self._thrusters) > self._curr_thruster_index + 1
            else 0
        )
        self.theme = self.get_curr_thruster().player_theme

    @on_key_press(MovementKeys.UP)
    def _move_up(self) -> None:
        if self.velocity.y >= self._get_max_speed():
            return self.set_last_known_direction()

        self.velocity = (self.velocity + VectorF(0, self._get_accel())).as_vector()
        self.set_last_known_direction()

    @on_key_press(MovementKeys.DOWN)
    def _move_down(self) -> None:
        if self.velocity.y <= -self._get_max_speed():
            return self.set_last_known_direction()

        self.velocity = (self.velocity + VectorF(0, -self._get_accel())).as_vector()
        self.set_last_known_direction()

    @on_key_press(MovementKeys.LEFT)
    def _move_left(self) -> None:
        if self.velocity.x <= -self._get_max_speed():
            return self.set_last_known_direction()

        self.velocity = (self.velocity + VectorF(-self._get_accel(), 0)).as_vector()
        self.set_last_known_direction()

    @on_key_press(MovementKeys.RIGHT)
    def _move_right(self) -> None:
        if self.velocity.x >= self._get_max_speed():
            return self.set_last_known_direction()

        self.velocity = (self.velocity + VectorF(self._get_accel(), 0)).as_vector()
        self.set_last_known_direction()

    ################
    """ CHEATS!! """

    ################
    @on_key_press(CheatKeys.KILL_MONSTERS)
    def _kill_all_monsters(self) -> None:
        for e in self._engine.scenario.enemies:
            e.die()
