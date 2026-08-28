from abc import abstractmethod
from typing import TYPE_CHECKING

from model.base import Point2F, Vector2F
from model.theme import Theme

if TYPE_CHECKING:
    from physics2d.scenario.scenario import Scenario


class Entity:
    position: Point2F
    velocity: Vector2F

    theme: Theme

    density: float
    volume: float
    name: str | None

    def __init__(
        self,
        scenario: "Scenario",
        name: str | None,
        density: int = 1,
        position: Point2F = (0, 0),
        velocity: Vector2F = (0, 0),
        theme: Theme = Theme(),
    ):
        self.scenario = scenario
        self.position = position
        self.velocity = velocity
        self.theme = theme
        self.density = density
        self.name = name

        # volume depends on the type of entity

    @abstractmethod
    def return_render_info(cls) -> None:
        # Each entity should do its thing
        raise NotImplementedError(f"{cls.name or 'UnknownEntity'} must have a render method")
