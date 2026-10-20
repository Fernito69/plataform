from dataclasses import dataclass, field

from physics2d.model.shared import RenderInfo


@dataclass
class HealthBarSnapshot:
    """A health bar already resolved to a screen position and a list of pixels.

    Everything that needs live entity/engine state (health, position, camera) is
    resolved when the snapshot is taken. Blending it with whatever ends up
    underneath happens at render time, since that needs the converted screen data.
    """

    y: int
    x_start: int
    pixels: list[str]
    with_special_chars: bool


@dataclass
class FrameSnapshot:
    """Everything the render stage needs for one frame, and nothing else.

    This has to stay self-contained: once it is handed over, the render stage
    never reads the scenario, the entities or the engine again, so the next frame
    can be calculated while this one is still being drawn (see pipeline.py).
    """

    screen_buffer: list[list[list[RenderInfo]]]
    x_res: int
    y_res: int
    health_bars: list[HealthBarSnapshot] = field(default_factory=list)
    hud: str | None = None
