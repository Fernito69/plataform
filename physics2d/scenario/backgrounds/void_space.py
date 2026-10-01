from typing import TYPE_CHECKING

from physics2d.scenario.background import Background, BgLayer

if TYPE_CHECKING:
    from physics2d.physics2d import Physics2D


class VoidSpace(Background):
    """N O T H I N G N E S S (good for performance)"""

    def __init__(self, engine: "Physics2D") -> None:
        self._engine = engine
        layers = self._init_layers()
        super().__init__(engine, layers)

    def _init_layers(self) -> list[BgLayer]:
        layers: list[BgLayer] = []

        return layers


def get_void_space(engine: "Physics2D") -> VoidSpace:
    return VoidSpace(engine)
