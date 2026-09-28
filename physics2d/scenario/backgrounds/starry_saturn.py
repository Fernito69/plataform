from typing import TYPE_CHECKING

from physics2d.scenario.background import Background, BgLayer
from physics2d.scenario.backgrounds.saturn_rings import get_saturn_rings
from physics2d.scenario.backgrounds.starry_space import get_starry_background

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class StarrySaturn(Background):
    """Saturn plus stars, shit doesn't work"""

    def __init__(self, engine: "Physics2D") -> None:
        self._engine = engine
        layers = self._init_layers()

        super().__init__(
            engine,
            layers,
            additional_backgrounds=self._additional_backgrounds,
            scroll_vertically=False,
        )

    def _init_layers(self) -> list[BgLayer]:
        self._additional_backgrounds = [
            get_starry_background(self._engine),
            get_saturn_rings(self._engine),
        ]
        return []


def get_starry_saturn(engine: "Physics2D") -> StarrySaturn:
    return StarrySaturn(engine)
