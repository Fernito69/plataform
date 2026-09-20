from typing import TYPE_CHECKING

from pynput import mouse

from model.base import PointF, VectorF
from model.shared import MouseHandler
from model.theme import RGB, Theme
from physics2d.constants import X_RESOLUTION_PHYSICS, Y_RESOLUTION_PHYSICS
from physics2d.entities.base import PhysicsEntity
from physics2d.shape.line import Line
from system import consume_mouse_movement

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D

_CROSSHAIR_THEME = Theme(
    color=RGB(20, 255, 20),
    bg_color=RGB(120, 255, 255),
)
_CROSSHAIR_SHOOTING_THEME = Theme(color=RGB(255, 0, 0))

_DOT_SIZE = 1
_HAIR_SIZE = 4
_HAIR_OFFSET = 5

_MOUSE_SENSITIVITY = 0.2


# TODO: this moves similar to player, should share a base class
class Crosshair(PhysicsEntity, MouseHandler):
    def __init__(
        self,
        engine: "Physics2D",
        position: PointF = PointF(X_RESOLUTION_PHYSICS / 2, Y_RESOLUTION_PHYSICS / 2),
        velocity=VectorF(0, 0),
        density: float = 1,
    ):
        super().__init__(
            name="Crosshair",
            position=position,
            initial_velocity=velocity,
            density=density,
            size=_DOT_SIZE,
            theme=_CROSSHAIR_THEME,
            engine=engine,
        )
        self._engine = engine
        self.center = position
        self.position = position
        self.radius = _DOT_SIZE
        self.theme = _CROSSHAIR_THEME
        self.velocity = velocity
        self.name = "Crosshair"

        # make the cross:
        def _make_line(l: tuple[tuple[float, float], tuple[float, float]]):
            return Line(
                points=(
                    self.center + PointF(l[0][0], l[0][1]),
                    self.center + PointF(l[1][0], l[1][1]),
                ),
                thickness=1,
                theme=Theme(_CROSSHAIR_THEME.bg_color),
                engine=self._engine,
            )

        self.extra_shapes = [
            _make_line(((0, _HAIR_OFFSET), (0, _HAIR_OFFSET + _HAIR_SIZE))),
            _make_line(((_HAIR_OFFSET, 0), (_HAIR_OFFSET + _HAIR_SIZE, 0))),
            _make_line(((0, -_HAIR_OFFSET), (0, -_HAIR_OFFSET - _HAIR_SIZE))),
            _make_line(((-_HAIR_OFFSET, 0), (-_HAIR_OFFSET - _HAIR_SIZE, 0))),
        ]
        # give a lil offset:
        self.center -= PointF(_DOT_SIZE/2, _DOT_SIZE/2)

    ##############
    """MOVEMENT"""
    ##############

    def do_your_thing(self) -> None:
        self._handle_mouse_input()
        self._handle_color()

        dx, dy = consume_mouse_movement()

        if dx != 0 or dy != 0:
            self._move_by(
                VectorF(
                    dx * _MOUSE_SENSITIVITY,
                    -dy * _MOUSE_SENSITIVITY,
                )
            )

    def _handle_color(self) -> None:
        curr_weapon = self._engine.scenario.player.get_curr_weapon()
        _is_pressing_trigger = self._is_mouse_pressed(mouse.Button.left)

        _og_color = (
            _CROSSHAIR_SHOOTING_THEME.color if _is_pressing_trigger else _CROSSHAIR_THEME.color
        ) or RGB()

        _initial_intensity = 0.1 if _is_pressing_trigger else 0.2
        _target_intensity = 0.9 if _is_pressing_trigger else 0.6

        if not curr_weapon.can_shoot():
            _factor = curr_weapon.get_life_time_ellapsed_ratio()
            _target_color = (
                _og_color.with_intensity(1 if _is_pressing_trigger else 0.6)
            ).with_intensity(_target_intensity)
            _final_color = (
                RGB(110, 110, 110)
                if _is_pressing_trigger or not _CROSSHAIR_SHOOTING_THEME.color
                else _CROSSHAIR_SHOOTING_THEME.color
            ).with_intensity(_initial_intensity).with_intensity(
                _factor
            ) + _target_color.with_intensity(1 - _factor)
            self.theme = Theme(_final_color)
        elif not _is_pressing_trigger:
            self.theme = Theme(_og_color)

    def _move_by(self, vector: VectorF) -> None:
        new_center = self.center + vector

        if new_center.y >= Y_RESOLUTION_PHYSICS:
            new_center.y = Y_RESOLUTION_PHYSICS - 1
        if new_center.x >= X_RESOLUTION_PHYSICS:
            new_center.x = X_RESOLUTION_PHYSICS - 1
        if new_center.x < 0:
            new_center.x = 0
        if new_center.y < 0:
            new_center.y = 0

        final_vector = (new_center - self.center).as_vector()

        self.center = new_center
        self.position = new_center

        for p in self.extra_shapes:
            if not isinstance(p, Line):
                continue
            p._move_by(final_vector)
