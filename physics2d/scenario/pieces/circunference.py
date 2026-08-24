import math
from dataclasses import dataclass
from typing import Callable

from factories.theme import White
from model.base import Point2, Vector2
from model.theme import Theme
from physics2d.model.base import RenderInfo
from physics2d.scenario.piece import ScenarioPiece


@dataclass
class GetCircunferenceEquationResponse:
    get_ys: Callable[[float], tuple[float, float] | tuple[None, None]]
    get_xs: Callable[[float], tuple[float, float] | tuple[None, None]]


class Circunference(ScenarioPiece):
    center: Point2
    radius: float

    def __init__(
        self,
        center: Point2,
        radius: float,
        theme: Theme = Theme(),
        angle: float = 0,
        affected_by_gravity: bool = False,
        initial_velocity: Vector2 = (0, 0),
        own_gravity: float | None = None,
        secondary_theme: Theme | None = None,
        floating_multi: float = 0,
    ):
        super().__init__(
            name="Circle",
            theme=theme,
            angle=angle,
            initial_velocity=initial_velocity,
            affected_by_gravity=affected_by_gravity,
            own_gravity=own_gravity,
            secondary_theme=secondary_theme,
            floating_multi=floating_multi,
        )
        self.center = center
        self.radius = radius

    def apply_movement(self) -> None:
        self._float_around()

        if not any(a != 0 for a in self.velocity):
            return
        self.center = (self.center[0] + self.velocity[0], self.center[1] + self.velocity[1])

    def get_circunference_equations(
        self,
    ) -> GetCircunferenceEquationResponse:
        def get_ys(x: float) -> tuple[float, float] | tuple[None, None]:
            root_arg = self.radius**2 - (x - self.center[0]) ** 2
            if root_arg < 0:
                return (None, None)
            root = root_arg**0.5
            return (self.center[1] - root, self.center[1] + root)

        def get_xs(y: float) -> tuple[float, float] | tuple[None, None]:
            root_arg = self.radius**2 - (y - self.center[1]) ** 2
            if root_arg < 0:
                return (None, None)
            root = root_arg**0.5
            return (self.center[0] - root, self.center[0] + root)

        return GetCircunferenceEquationResponse(get_xs=get_xs, get_ys=get_ys)

    def return_render_info(self) -> list[RenderInfo]:
        piece_info = []
        min_x, max_x = sorted(
            (
                self.center[0] + self.radius,
                self.center[0] - self.radius,
            )
        )
        min_y, max_y = sorted(
            (
                self.center[1] + self.radius,
                self.center[1] - self.radius,
            )
        )

        eq = self.get_circunference_equations()

        for x in range(math.floor(min_x - 1), math.ceil(max_x + 1)):
            y1, y2 = eq.get_ys(x)

            # TODO: here we need to do something to make the upper border render
            if y1 is None or y2 is None:
                continue

            for y in range(math.floor(min_y - 1), math.ceil(max_y + 1)):
                x1, x2 = eq.get_xs(y)

                if x1 is None or x2 is None:
                    continue

                # TODO: good proxy with good performance, but maybe can be done better
                distance = min(
                    max(
                        0,
                        y - y2,
                        y1 - y,
                    ),
                    max(
                        0,
                        x - x2,
                        x1 - x,
                    ),
                )
                if distance > 1:
                    continue

                piece_info.append(
                    RenderInfo(
                        distance_to_pixel_center=distance,
                        color=self.theme.color or White(),
                        point=(x, y),
                    )
                )

        return piece_info
